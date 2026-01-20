import psycopg2
import hashlib
import secrets
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict, Any
from models import *

class Database:
    def __init__(self, db_params: Dict[str, Any]):
        self.db_params = db_params
        self.connection = None

        self.seat_config = {
            'BUS': {
                'rows': 3,
                'seats_per_row': 4,
                'seat_letters': ['A', 'B', 'C', 'D']
            },
            'ECO': {
                'rows': 10,
                'seats_per_row': 4,
                'seat_letters': ['A', 'B', 'C', 'D']
            }
        }
    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_params)
            return True
        except Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def create_seats_for_flight(self, flight_id: int) -> bool:
        try:
            with self.connection.cursor() as cursor:
                for row in range(1, self.seat_config['BUS']['rows'] + 1):
                    for letter in self.seat_config['BUS']['seat_letters']:
                        cursor.execute(
                            """INSERT INTO place (id_flight, seat_class, row_number, seat_letter, number_class, number_place)
                               VALUES (%s, 'BUS', %s, %s, 'BUS', %s)""",
                            (flight_id, row, letter, f"{row}{letter}")
                        )

                for row in range(1, self.seat_config['ECO']['rows'] + 1):
                    for letter in self.seat_config['ECO']['seat_letters']:
                        cursor.execute(
                            """INSERT INTO place (id_flight, seat_class, row_number, seat_letter, number_class, number_place)
                               VALUES (%s, 'ECO', %s, %s, 'ECO', %s)""",
                            (flight_id, row, letter, f"{row}{letter}")
                        )

                self.connection.commit()
                return True
        except Error as e:
            print(f"Ошибка создания мест: {e}")
            return False

    def validate_seat(self, seat_class: str, row_number: int, seat_letter: str) -> bool:
        config = self.seat_config.get(seat_class.upper())
        if not config:
            return False

        if row_number < 1 or row_number > config['rows']:
            return False

        if seat_letter.upper() not in config['seat_letters']:
            return False

        return True

    def get_seat_by_number(self, flight_id: int, seat_number: str) -> Optional[Seat]:
        with self.connection.cursor() as cursor:
            import re
            match = re.match(r'(\d+)([A-Z])', seat_number.upper())
            if match:
                row = int(match.group(1))
                letter = match.group(2)
                cursor.execute(
                    """SELECT id, id_flight, seat_class, row_number, seat_letter
                       FROM place 
                       WHERE id_flight = %s AND row_number = %s AND seat_letter = %s""",
                    (flight_id, row, letter)
                )
                result = cursor.fetchone()

                if result:
                    return Seat(
                        id=result[0],
                        id_flight=result[1],
                        seat_class=result[2],
                        row_number=result[3],
                        seat_letter=result[4]
                    )
            return None

    def get_all_places_for_flight(self, flight_id: int) -> List[Seat]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT id, id_flight, seat_class, row_number, seat_letter
                   FROM place 
                   WHERE id_flight = %s
                   ORDER BY 
                       CASE seat_class WHEN 'BUS' THEN 1 ELSE 2 END,
                       row_number,
                       seat_letter""",
                (flight_id,)
            )
            rows = cursor.fetchall()
            seats = []
            for row in rows:
                seats.append(Seat(
                    id=row[0],
                    id_flight=row[1],
                    seat_class=row[2],
                    row_number=row[3],
                    seat_letter=row[4]
                ))
            return seats

    def get_available_places(self, flight_id: int) -> List[Dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT pl.id, pl.seat_class, pl.row_number, pl.seat_letter,
                CONCAT(pl.row_number, pl.seat_letter, ' (', pl.seat_class, ')') as display_name
            FROM place pl
            WHERE pl.id_flight = %s 
            AND pl.id NOT IN (
                SELECT id_place FROM booking 
                WHERE id_flight = %s AND status = true
            )
            ORDER BY 
                CASE pl.seat_class WHEN 'BUS' THEN 1 ELSE 2 END,
                pl.row_number,
                pl.seat_letter
            """
            cursor.execute(query, (flight_id, flight_id))
            return cursor.fetchall()

    def get_seat_statistics(self, flight_id: int) -> Dict:
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.seat_class,
                    COUNT(p.id) as total,
                    COUNT(DISTINCT b.id_place) as booked
                FROM place p
                LEFT JOIN booking b ON p.id = b.id_place 
                    AND b.status = true
                    AND b.id_flight = %s
                WHERE p.id_flight = %s
                GROUP BY p.seat_class
            """, (flight_id, flight_id))

            result = {}
            for row in cursor.fetchall():
                seat_class = row[0]
                total = row[1]
                booked = row[2]

                percentage = round((booked / total) * 100, 2) if total > 0 else 0

                result[seat_class] = {
                    'total': total,
                    'booked': booked,
                    'available': total - booked,
                    'percentage': percentage
                }

            # Гарантируем наличие обоих классов
            if 'BUS' not in result:
                result['BUS'] = {
                    'total': 12,  # 3 ряда × 4 места = 12
                    'booked': 0,
                    'available': 12,
                    'percentage': 0
                }

            if 'ECO' not in result:
                result['ECO'] = {
                    'total': 40,  # 10 рядов × 4 места = 40
                    'booked': 0,
                    'available': 40,
                    'percentage': 0
                }

            return result

    def get_all_companies(self) -> List[Company]:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM company ORDER BY id")
            rows = cursor.fetchall()
            companies = []
            for row in rows:
                company_dict = {
                    'id': row[0],
                    'name_company': row[1]
                }
                companies.append(Company(**company_dict))
            return companies

    def add_company(self, name_company: str) -> Optional[int]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO company (name_company) VALUES (%s) RETURNING id",
                (name_company,)
            )
            self.connection.commit()
            return cursor.fetchone()[0]

    def delete_company(self, company_id: int) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM company WHERE id = %s", (company_id,))
                self.connection.commit()
                return cursor.rowcount > 0
        except Error:
            return False

    def get_all_airplanes(self) -> List[Airplane]:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM airplane ORDER BY id")
            rows = cursor.fetchall()
            airplanes = []
            for row in rows:
                airplane_dict = {
                    'id': row[0],
                    'name_airplane': row[1],
                    'id_company': row[2]
                }
                airplanes.append(Airplane(**airplane_dict))
            return airplanes

    def add_airplane(self, name_airplane: str, id_company: int) -> Optional[int]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO airplane (name_airplane, id_company) VALUES (%s, %s) RETURNING id",
                (name_airplane, id_company)
            )
            self.connection.commit()
            return cursor.fetchone()[0]

    def get_all_airports(self) -> List[Airport]:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM airport ORDER BY id")
            rows = cursor.fetchall()
            airports = []
            for row in rows:
                airport_dict = {
                    'id': row[0],
                    'start_airport': row[1],
                    'finish_airport': row[2]
                }
                airports.append(Airport(**airport_dict))
            return airports

    def add_airport(self, start_airport: str, finish_airport: str) -> Optional[int]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO airport (start_airport, finish_airport) VALUES (%s, %s) RETURNING id",
                (start_airport, finish_airport)
            )
            self.connection.commit()
            return cursor.fetchone()[0]

    def get_all_flights(self) -> List[Dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT f.id, f.number_flight, a.name_airplane, 
                   ap.start_airport || ' - ' || ap.finish_airport as airport,
                   f.time_flight, c.name_company,
                   f.id_airplane, f.id_airport
            FROM flight f
            JOIN airplane a ON f.id_airplane = a.id
            JOIN airport ap ON f.id_airport = ap.id
            JOIN company c ON a.id_company = c.id
            ORDER BY f.id
            """
            cursor.execute(query)
            return cursor.fetchall()

    def add_flight(self, id_airplane: int, id_airport: int,
                   number_flight: int, time_flight: str) -> Optional[int]:
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(
                    """INSERT INTO flight (id_airplane, id_airport, number_flight, time_flight) 
                       VALUES (%s, %s, %s, %s) RETURNING id""",
                    (id_airplane, id_airport, number_flight, time_flight)
                )
                flight_id = cursor.fetchone()[0]

                self.create_seats_for_flight(flight_id)

                self.connection.commit()
                return flight_id
            except Error as e:
                self.connection.rollback()
                print(f"Ошибка добавления рейса: {e}")
                return None

    def delete_flight(self, flight_id: int) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM booking WHERE id_flight = %s", (flight_id,))
                cursor.execute("DELETE FROM place WHERE id_flight = %s", (flight_id,))
                cursor.execute("DELETE FROM flight WHERE id = %s", (flight_id,))
                self.connection.commit()
                return cursor.rowcount > 0
        except Error:
            self.connection.rollback()
            return False

    def find_seat_by_details(self, flight_id: int, seat_class: str, row: int, letter: str) -> Optional[Seat]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT id, id_flight, seat_class, row_number, seat_letter
                   FROM place 
                   WHERE id_flight = %s 
                     AND seat_class = %s 
                     AND row_number = %s 
                     AND seat_letter = %s""",
                (flight_id, seat_class.upper(), row, letter.upper())
            )
            result = cursor.fetchone()

            if result:
                return Seat(
                    id=result[0],
                    id_flight=result[1],
                    seat_class=result[2],
                    row_number=result[3],
                    seat_letter=result[4]
                )
            return None

    def is_seat_available(self, seat_id: int, flight_id: int) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT 1 FROM booking 
                   WHERE id_place = %s AND id_flight = %s AND status = true""",
                (seat_id, flight_id)
            )
            result = cursor.fetchone()
            return result is None

    def add_passenger(self, first_name: str, second_name: str,
                      number_phone: str, number_passport: str) -> Optional[int]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO passenger (first_name, second_name, number_phone, number_passport) 
                   VALUES (%s, %s, %s, %s) RETURNING id""",
                (first_name, second_name, number_phone, number_passport)
            )
            self.connection.commit()
            return cursor.fetchone()[0]

    def delete_passenger(self, passenger_id: int) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM passenger WHERE id = %s", (passenger_id,))
                self.connection.commit()
                return cursor.rowcount > 0
        except Error:
            return False

    def get_all_passengers(self) -> List[Passenger]:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM passenger ORDER BY id")
            rows = cursor.fetchall()
            passengers = []
            for row in rows:
                passenger_dict = {
                    'id': row[0],
                    'first_name': row[1],
                    'second_name': row[2],
                    'number_phone': row[3],
                    'number_passport': row[4]
                }
                passengers.append(Passenger(**passenger_dict))
            return passengers

    def get_all_bookings(self) -> List[Dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT b.id, 
                f.number_flight, 
                p.first_name || ' ' || p.second_name as passenger,
                CONCAT(pl.seat_class, pl.row_number, pl.seat_letter) as seat,
                b.booking_time, 
                b.status,
                b.id_flight, b.id_place, b.id_passenger
            FROM booking b
            JOIN flight f ON b.id_flight = f.id
            JOIN passenger p ON b.id_passenger = p.id
            JOIN place pl ON b.id_place = pl.id
            ORDER BY b.booking_time DESC
            """
            cursor.execute(query)
            return cursor.fetchall()

    def create_booking(self, id_flight: int, id_place: int,
                       id_passenger: int, status: bool = True) -> Optional[int]:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO booking (id_flight, id_place, id_passenger, status) 
                       VALUES (%s, %s, %s, %s) RETURNING id""",
                    (id_flight, id_place, id_passenger, status)
                )
                self.connection.commit()
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Ошибка при создании бронирования: {e}")
            return None

    def cancel_booking_by_id(self, booking_id: int) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("CALL cancel_booking_by_id(%s)", (booking_id,))
                self.connection.commit()
                return True
        except Error as e:
            print(f"Ошибка отмены бронирования: {e}")
            self.connection.rollback()
            return False

    def search_flights(self, start_airport: str = "", finish_airport: str = "") -> List[Dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT f.id, f.number_flight, ap.start_airport, ap.finish_airport, 
                   f.time_flight, c.name_company
            FROM flight f
            JOIN airplane a ON f.id_airplane = a.id
            JOIN airport ap ON f.id_airport = ap.id
            JOIN company c ON a.id_company = c.id
            WHERE ap.start_airport ILIKE %s AND ap.finish_airport ILIKE %s
            """
            cursor.execute(query, (f'%{start_airport}%', f'%{finish_airport}%'))
            return cursor.fetchall()

    def get_flights_by_company(self) -> List[tuple]:
        with self.connection.cursor() as cursor:
            query = """
            SELECT c.name_company, COUNT(f.id) as flight_count
            FROM company c
            LEFT JOIN airplane a ON c.id = a.id_company
            LEFT JOIN flight f ON a.id = f.id_airplane
            GROUP BY c.name_company
            ORDER BY flight_count DESC
            """
            cursor.execute(query)
            return cursor.fetchall()

    def get_occupancy_report(self) -> List[tuple]:
        with self.connection.cursor() as cursor:
            query = """
            SELECT f.number_flight, 
                   COUNT(pl.id) as total_seats,
                   COUNT(b.id) as booked_seats,
                   ROUND(COUNT(b.id) * 100.0 / COUNT(pl.id), 2) as occupancy_rate
            FROM flight f
            LEFT JOIN place pl ON f.id = pl.id_flight
            LEFT JOIN booking b ON pl.id = b.id_place AND b.status = true
            GROUP BY f.number_flight
            ORDER BY occupancy_rate DESC
            """
            cursor.execute(query)
            return cursor.fetchall()

    def get_bookings_by_day(self) -> List[tuple]:
        with self.connection.cursor() as cursor:
            query = """
            SELECT DATE(booking_time) as booking_date, 
                   COUNT(*) as bookings_count
            FROM booking
            WHERE status = true
            GROUP BY DATE(booking_time)
            ORDER BY booking_date DESC
            LIMIT 30
            """
            cursor.execute(query)
            return cursor.fetchall()

    def get_popular_routes(self) -> List[tuple]:
        with self.connection.cursor() as cursor:
            query = """
            SELECT ap.start_airport, ap.finish_airport, 
                   COUNT(b.id) as bookings_count
            FROM booking b
            JOIN flight f ON b.id_flight = f.id
            JOIN airport ap ON f.id_airport = ap.id
            WHERE b.status = true
            GROUP BY ap.start_airport, ap.finish_airport
            ORDER BY bookings_count DESC
            LIMIT 10
            """
            cursor.execute(query)
            return cursor.fetchall()

    def authenticate_user(self, nickname: str, password: str):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, nickname, role, password_hash FROM users WHERE nickname = %s",
                (nickname,)
            )
            result = cursor.fetchone()

            if not result:
                return None

            stored_hash = result[3]
            if not stored_hash:
                return None

            if '$' in stored_hash:
                try:
                    salt, stored_password_hash = stored_hash.split('$', 1)
                    test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                    if test_hash == stored_password_hash:
                        return {
                            'id': result[0],
                            'nickname': result[1],
                            'role': result[2],
                            'admin': result[2] == 'ADMIN',
                            'senior': result[2] in ['ADMIN', 'SENIOR']
                        }
                except:
                    pass

            if stored_hash == password:
                return {
                    'id': result[0],
                    'nickname': result[1],
                    'role': result[2],
                    'admin': result[2] == 'ADMIN',
                    'senior': result[2] in ['ADMIN', 'SENIOR']
                }

            return None

    def check_user_exists(self, nickname: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "select id from users where nickname = %s",
                (nickname,)
            )
            return cursor.fetchone() is not None

    def register_user(self, nickname: str, password: str):
        try:
            with self.connection.cursor() as cursor:
                salt = secrets.token_hex(16)
                password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                full_hash = f"{salt}${password_hash}"

                cursor.execute(
                    "insert into users (nickname, password_hash, admin) values (%s, %s, false) returning id",
                    (nickname, full_hash)
                )
                self.connection.commit()
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"ошибка регистрации: {e}")
            return None

    def get_all_users(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, nickname, role FROM users ORDER BY id")
            rows = cursor.fetchall()
            users = []
            for row in rows:
                users.append({
                    'id': row[0],
                    'nickname': row[1],
                    'role': row[2],
                    'admin': row[2] == 'ADMIN',
                    'senior': row[2] in ['ADMIN', 'SENIOR']
                })
            return users

    def update_user_admin(self, user_id: int, is_admin: bool) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET admin = %s WHERE id = %s",
                    (is_admin, user_id)
                )
                self.connection.commit()
                return cursor.rowcount > 0
        except Error:
            return False

    def delete_user(self, user_id: int) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                self.connection.commit()
                return cursor.rowcount > 0
        except Error:
            return False

    def get_current_user_id(self):
        if hasattr(self, 'current_user'):
            return self.current_user.get('id')
        return None

    def get_report_company_flights(self) -> List[Dict]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        c.name_company AS "Авиакомпания",
                        COUNT(DISTINCT f.id) AS "Количество рейсов",
                        COUNT(DISTINCT a.id) AS "Количество самолетов"
                    FROM company c
                    LEFT JOIN airplane a ON c.id = a.id_company
                    LEFT JOIN flight f ON a.id = f.id_airplane
                    GROUP BY c.name_company
                    ORDER BY COUNT(DISTINCT f.id) DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка в get_report_company_flights: {e}")
            self.connect()
            return []

    def get_report_passenger_stats(self, limit: int = 20) -> List[Dict]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM report_passengers_simple 
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка в get_report_passenger_stats: {e}")
            return []

    def get_report_seat_occupancy(self) -> List[Dict]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM report_seat_occupancy_simple")
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка в get_report_seat_occupancy: {e}")
            return []

    def get_report_seat_class_stats(self) -> List[Dict]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM report_seat_class_stats")
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка в get_report_seat_class_stats: {e}")
            return []
    def update_flight(self, flight_id: int, id_airplane: int = None, id_airport: int = None,
                      number_flight: int = None, time_flight: str = None) -> bool:
        try:
            with self.connection.cursor() as cursor:
                updates = []
                params = []

                if id_airplane is not None:
                    updates.append("id_airplane = %s")
                    params.append(id_airplane)

                if id_airport is not None:
                    updates.append("id_airport = %s")
                    params.append(id_airport)

                if number_flight is not None:
                    updates.append("number_flight = %s")
                    params.append(number_flight)

                if time_flight is not None:
                    updates.append("time_flight = %s")
                    params.append(time_flight)

                if not updates:
                    return False

                query = f"UPDATE flight SET {', '.join(updates)} WHERE id = %s"
                params.append(flight_id)

                cursor.execute(query, tuple(params))
                self.connection.commit()

                return cursor.rowcount > 0
        except Error as e:
            print(f"Ошибка обновления рейса: {e}")
            self.connection.rollback()
            return False

    def cancel_all_flight_bookings(self, flight_id: int) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("CALL cancel_all_flight_bookings(%s)", (flight_id,))
                self.connection.commit()
                return True
        except Error as e:
            print(f"Ошибка отмены бронирований: {e}")
            self.connection.rollback()
            return False

    def confirm_cancelled_booking(self, booking_id: int) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("CALL confirm_cancelled_booking(%s)", (booking_id,))
                self.connection.commit()
                return True
        except Error as e:
            print(f"Ошибка подтверждения бронирования: {e}")
            self.connection.rollback()
            return False

    def update_user_role(self, user_id: int, role: str) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET role = %s WHERE id = %s",
                    (role, user_id)
                )
                self.connection.commit()
                return cursor.rowcount > 0
        except Error:
            return False

