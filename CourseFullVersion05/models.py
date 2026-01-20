from dataclasses import dataclass
from datetime import datetime, time

@dataclass
class Company:
    id: int
    name_company: str

@dataclass
class Airplane:
    id: int
    name_airplane: str
    id_company: int

@dataclass
class Airport:
    id: int
    start_airport: str
    finish_airport: str

@dataclass
class Flight:
    id: int
    id_airplane: int
    id_airport: int
    number_flight: int
    time_flight: time

@dataclass
class Place:
    id: int
    id_flight: int
    number_class: str
    number_place: str

@dataclass
class Passenger:
    id: int
    first_name: str
    second_name: str
    number_phone: str
    number_passport: str

@dataclass
class Booking:
    id: int
    id_flight: int
    id_place: int
    id_passenger: int
    booking_time: datetime
    status: bool


@dataclass
class Seat:
    id: int
    id_flight: int
    seat_class: str  # 'BUS' или 'ECO'
    row_number: int
    seat_letter: str  # 'A', 'B', 'C', 'D'

    @property
    def number_place(self) -> str:
        return f"{self.row_number}{self.seat_letter}"

    @property
    def number_class(self) -> str:
        return self.seat_class