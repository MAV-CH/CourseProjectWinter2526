import unittest
from models import Company, Airplane, Passenger, Seat, Flight, Airport, Booking
from datetime import datetime, time
from database import Database


class Tests(unittest.TestCase):
    def test_1_company_model(self):
        company = Company(id=1, name_company="Аэрофлот")
        self.assertEqual(company.name_company, "Аэрофлот")
        print("✅ test_1_company_model - OK")

    def test_2_airplane_model(self):
        airplane = Airplane(id=1, name_airplane="Boeing 737", id_company=1)
        self.assertEqual(airplane.name_airplane, "Boeing 737")
        print("✅ test_2_airplane_model - OK")

    def test_3_passenger_model(self):
        passenger = Passenger(
            id=1,
            first_name="Иван",
            second_name="Иванов",
            number_phone="+79161234567",
            number_passport="40 01 123456"
        )
        self.assertEqual(passenger.first_name, "Иван")
        self.assertEqual(passenger.second_name, "Иванов")
        print("✅ test_3_passenger_model - OK")

    def test_4_seat_model(self):
        seat = Seat(
            id=1,
            id_flight=100,
            seat_class='BUS',
            row_number=2,
            seat_letter='A'
        )
        self.assertEqual(seat.number_place, '2A')
        self.assertEqual(seat.seat_class, 'BUS')
        print("✅ test_4_seat_model - OK")

    def test_5_seat_validation(self):
        db = Database({})
        self.assertTrue(db.validate_seat('BUS', 1, 'A'))
        self.assertTrue(db.validate_seat('ECO', 10, 'D'))
        self.assertFalse(db.validate_seat('BUS', 4, 'A'))
        self.assertFalse(db.validate_seat('ECO', 1, 'Z'))
        print("✅ test_5_seat_validation - OK")

    def test_6_flight_model(self):
        flight = Flight(
            id=1,
            id_airplane=5,
            id_airport=3,
            number_flight=777,
            time_flight=time(14, 30)  # 14:30
        )
        self.assertEqual(flight.number_flight, 777)
        self.assertEqual(flight.time_flight.hour, 14)
        self.assertEqual(flight.time_flight.minute, 30)
        print("✅ test_6_flight_model - OK")

    def test_7_airport_model(self):
        airport = Airport(
            id=1,
            start_airport="SVO",
            finish_airport="LED"
        )
        self.assertEqual(airport.start_airport, "SVO")
        self.assertEqual(airport.finish_airport, "LED")
        self.assertEqual(len(airport.start_airport), 3)
        print("✅ test_7_airport_model - OK")

    def test_8_booking_model(self):
        booking_time = datetime(2024, 1, 15, 10, 30, 0)
        booking = Booking(
            id=1,
            id_flight=100,
            id_place=50,
            id_passenger=25,
            booking_time=booking_time,
            status=True
        )
        self.assertEqual(booking.id_flight, 100)
        self.assertEqual(booking.id_passenger, 25)
        self.assertTrue(booking.status)
        self.assertEqual(booking.booking_time.year, 2024)
        print("✅ test_8_booking_model - OK")

    def test_9_seat_number_generation(self):
        test_cases = [
            (1, 'A', '1A'),
            (2, 'B', '2B'),
            (10, 'C', '10C'),
            (3, 'D', '3D')
        ]

        for row, letter, expected in test_cases:
            generated = f"{row}{letter}"
            self.assertEqual(generated, expected,
                             f"Ряд {row}, место {letter} → {expected}")
        print("✅ test_9_seat_number_generation - OK")

    def test_10_different_seat_classes(self):
        db = Database({})

        bus_seat = Seat(
            id=1, id_flight=100,
            seat_class='BUS', row_number=1, seat_letter='A'
        )
        self.assertEqual(bus_seat.seat_class, 'BUS')

        eco_seat = Seat(
            id=2, id_flight=100,
            seat_class='ECO', row_number=5, seat_letter='C'
        )
        self.assertEqual(eco_seat.seat_class, 'ECO')

        self.assertNotEqual(bus_seat.seat_class, eco_seat.seat_class)
        self.assertEqual(bus_seat.number_class, 'BUS')
        self.assertEqual(eco_seat.number_class, 'ECO')
        print("✅ test_10_different_seat_classes - OK")



if __name__ == '__main__':
    unittest.main()