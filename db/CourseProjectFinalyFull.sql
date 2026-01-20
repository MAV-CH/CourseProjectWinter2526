create table company(
	id serial primary key,
	name_company varchar(25) not null
	);

create table airplane(
	id serial primary key,
	name_airplane varchar(25),
	id_company int not null,
	
	constraint fk_airplane_company
	foreign key (id_company) references company(id)
	);
	
create table airport(
 	id serial primary key,
 	start_airport char(3) not null,
 	finish_airport char(3) not null
	);
	
create table flight(
	id serial primary key,
	id_airplane int not null,
	id_airport int not null,
	number_flight int,
	time_flight time,
	
	constraint fk_flight_airplane
	foreign key (id_airplane) references airplane(id),
	
	constraint fk_flight_airport
	foreign key (id_airport) references airport(id)
	);

create table place(
	id serial primary key,
	id_flight int not null,
	seat_class seat_class,
	row_number integer,
	seat_letter char(1);
	
	constraint fk_place_flight
	foreign key (id_flight) references flight(id),
	
	add constraint check_seat_letter 
	check (seat_letter in ('A', 'B', 'C', 'D'))
	);
	
create table passenger(
	id serial primary key,
	first_name varchar(30),
	second_name varchar(30),
	number_phone varchar(20),
	number_passport varchar(20)
	);	
	
create table booking(
	id serial primary key,
	id_flight int not null,
	id_place int not null,
	id_passenger int not null,
	booking_time timestamp default now(),
	status boolean,
	
	constraint fk_booking_flight
	foreign key (id_flight) references flight(id),
	
	constraint fk_booking_place
	foreign key (id_place) references place(id),
	
	constraint fk_booking_passenger
	foreign key (id_passenger) references passenger(id),
	
	constraint unique_place_per_flight
	unique (id_flight, id_place)
	);
	
create table users(
		id serial primary key,
		nickname varchar(30),
		password varchar(30),
		role varchar(20) default 'EMPLOYEE' check (role in ('ADMIN', 'SENIOR', 'EMPLOYEE'))
	);

create type seat_class as enum ('BUS', 'ECO');

create unique index idx_unique_seat on place 
(id_flight, row_number, seat_letter, seat_class);

drop type seat_class cascade;

alter table place 
drop column seat_class;

alter table place 
add constraint check_seat_letter 
check (seat_letter in ('A', 'B', 'C', 'D'));

-- 
create unique index idx_unique_seat on place 
(id_flight, row_number, seat_letter, seat_class);

--
alter table place 
add constraint check_business_rows 
check ((seat_class = 'BUS' and row_number between 1 and 3) or seat_class = 'ECO');

alter table place 
drop constraint check_business_rows;

alter table place 
add constraint check_economy_rows 
check ((seat_class = 'ECO' and row_number between 1 and 10) or seat_class = 'BUS');

alter table place 
drop constraint check_economy_rows;

--

create or replace view report_company_flights  as
select
    c.name_company as "Авиакомпания",
    count(distinct f.id) as "Количество рейсов",
    count(distinct a.id) as "Количество самолетов"
from company c
left join airplane a on c.id = a.id_company
left join flight f on a.id = f.id_airplane
group  by c.name_company
order by count(distinct f.id) desc;

select * from report_company_flights;
create view report_passengers_simple as
select 
    p.first_name || ' ' || p.second_name as "Пассажир",
    p.number_passport as "Паспорт",
    count(distinct b.id) as "Всего бронирований"
from passenger p
left join booking b on p.id = b.id_passenger
group by p.id, p.first_name, p.second_name, p.number_passport
order by count(distinct b.id) desc;

-- 
create view report_seat_occupancy_simple as
select 
    f.number_flight as "Номер рейса",
    ap.start_airport || ' → ' || ap.finish_airport as "Маршрут",
    count(b.id) as "Количество броней"
from flight f
join airport ap on f.id_airport = ap.id
left join booking b on f.id = b.id_flight and b.status = true
group by f.id, f.number_flight, ap.start_airport, ap.finish_airport
order by "Количество броней" desc;

--
create view report_seat_class_stats as
select 
    f.number_flight as "Номер рейса",
    pl.seat_class as "Класс места",
    count(pl.id) as "Всего мест",
    count(case when b.id is not null and b.status = true then 1 end) as "Занято мест",
    round(
        count(case when b.id is not null and b.status = true then 1 end) * 100.0 / count(pl.id), 
        2
    ) as "Процент занятости"
from flight f
join place pl on f.id = pl.id_flight
left join booking b on pl.id = b.id_place and b.status = true
group by f.number_flight, pl.seat_class
order by f.number_flight, pl.seat_class;

-- 
create or replace function create_airplane_seats(
    p_flight_id integer,
    p_business_rows integer default 3,
    p_economy_rows integer default 10
) returns void as $$
declare
    row_num integer;
    seat_letter char(1);
    seat_letters char[] := array['a', 'b', 'c', 'd'];
begin
    for row_num in 1..p_business_rows loop
        foreach seat_letter in array seat_letters loop
            insert into place (id_flight, seat_class, row_number, seat_letter)
            values (
                p_flight_id,
                'BUS',
                row_num,
                seat_letter
            );
        end loop;
    end loop;
    for row_num in 1..p_economy_rows loop
        foreach seat_letter in array seat_letters loop
            insert into place (id_flight, seat_class, row_number, seat_letter)
            values (
                p_flight_id,
                'ECO',
                row_num,
                seat_letter
            );
        end loop;
    end loop;
end;
$$ language plpgsql;

-- 
create or replace function create_seats_for_flight()
returns trigger as $$
begin
    if not exists (select 1 from place where id_flight = new.id) then
        perform create_airplane_seats(new.id);
    end if;
    return new;
end;
$$ language plpgsql;

-- 
create trigger tr_create_flight_seats
after insert on flight
for each row
execute function create_seats_for_flight();


-- Заполнение таблицы company (20 записей)
insert into company (name_company) values
('Аэрофлот'), ('S7 Airlines'), ('Победа'), ('Уральские авиалинии'),
('Россия'), ('Ямал'), ('Red Wings'), ('Азимут'),
('Nordwind Airlines'), ('Smartavia'), ('ИрАэро'), ('ЮВТ Аэро'),
('Северный ветер'), ('Алроса'), ('Газпромавиа'), ('UTair'),
('РусЛайн'), ('Ижавиа'), ('Костромское авиа'), ('Сибирь');

-- Заполнение таблицы airplane (30 записей)
insert into airplane (name_airplane, id_company) values
('Boeing 737-800', 1), ('Airbus A320', 1), ('Sukhoi Superjet', 1),
('Boeing 777-300', 2), ('Airbus A321', 2), ('Embraer E170', 2),
('Boeing 737-800', 3), ('Airbus A319', 3), ('Boeing 737-700', 4),
('Airbus A320neo', 5), ('Boeing 747-400', 6), ('Airbus A330', 7),
('Sukhoi Superjet', 8), ('Boeing 737-900', 9), ('Airbus A321neo', 10),
('Embraer E190', 11), ('Boeing 787', 12), ('Airbus A350', 13),
('Boeing 737 MAX', 14), ('Airbus A220', 15), ('Boeing 767', 16),
('Airbus A340', 17), ('Boeing 757', 18), ('Airbus A380', 19),
('Sukhoi Superjet', 20), ('Boeing 737-400', 1), ('Airbus A310', 2),
('Embraer E175', 3), ('Boeing 737-500', 4), ('Airbus A300', 5);

-- Заполнение таблицы airport (25 записей)
insert into airport (start_airport, finish_airport) values
('SVO', 'LED'), ('DME', 'AER'), ('VKO', 'KRR'), ('LED', 'SVO'),
('AER', 'DME'), ('KRR', 'VKO'), ('SVO', 'KZN'), ('DME', 'OVB'),
('VKO', 'ROV'), ('LED', 'KGD'), ('SVO', 'SVX'), ('DME', 'UFA'),
('VKO', 'KJA'), ('LED', 'MRV'), ('SVO', 'OMS'), ('DME', 'GOJ'),
('VKO', 'KEJ'), ('LED', 'NNN'), ('SVO', 'KUF'), ('DME', 'VVO'),
('VKO', 'IKT'), ('LED', 'KHV'), ('SVO', 'AAQ'), ('DME', 'ABA'),
('VKO', 'DYR');

-- Заполнение таблицы flight (30 записей)
insert into flight (id_airplane, id_airport, number_flight, time_flight) values
(1, 1, 1001, '08:30'), (2, 2, 1002, '10:15'), (3, 3, 1003, '12:45'),
(4, 4, 1004, '14:20'), (5, 5, 1005, '16:00'), (6, 6, 1006, '18:30'),
(7, 7, 1007, '20:15'), (8, 8, 1008, '22:00'), (9, 9, 1009, '06:45'),
(10, 10, 1010, '09:30'), (11, 11, 1011, '11:15'), (12, 12, 1012, '13:45'),
(13, 13, 1013, '15:20'), (14, 14, 1014, '17:00'), (15, 15, 1015, '19:30'),
(16, 16, 1016, '21:15'), (17, 17, 1017, '23:00'), (18, 18, 1018, '07:45'),
(19, 19, 1019, '10:30'), (20, 20, 1020, '12:15'), (21, 21, 1021, '14:45'),
(22, 22, 1022, '16:20'), (23, 23, 1023, '18:00'), (24, 24, 1024, '20:30'),
(25, 25, 1025, '22:15'), (26, 1, 1026, '06:00'), (27, 2, 1027, '08:45'),
(28, 3, 1028, '11:30'), (29, 4, 1029, '13:15'), (30, 5, 1030, '17:45');

-- Заполнение таблицы passenger (30 записей)
insert into passenger (first_name, second_name, number_phone, number_passport) values
('Иван', 'Иванов', '+79161234567', '40 01 123456'),
('Петр', 'Петров', '+79162345678', '40 02 234567'),
('Анна', 'Сидорова', '+79163456789', '40 03 345678'),
('Мария', 'Кузнецова', '+79164567890', '40 04 456789'),
('Сергей', 'Смирнов', '+79165678901', '40 05 567890'),
('Ольга', 'Попова', '+79166789012', '40 06 678901'),
('Алексей', 'Васильев', '+79167890123', '40 07 789012'),
('Елена', 'Морозова', '+79168901234', '40 08 890123'),
('Дмитрий', 'Новиков', '+79169012345', '40 09 901234'),
('Наталья', 'Федорова', '+79160123456', '40 10 012345'),
('Андрей', 'Волков', '+79161234560', '41 01 123450'),
('Татьяна', 'Алексеева', '+79162345601', '41 02 234560'),
('Михаил', 'Лебедев', '+79163456012', '41 03 345601'),
('Юлия', 'Семенова', '+79164560123', '41 04 456012'),
('Владимир', 'Егоров', '+79165601234', '41 05 560123'),
('Светлана', 'Павлова', '+79166012345', '41 06 601234'),
('Александр', 'Козлов', '+79167123456', '41 07 712345'),
('Екатерина', 'Степанова', '+79168234567', '41 08 823456'),
('Николай', 'Николаев', '+79169345678', '41 09 934567'),
('Ирина', 'Орлова', '+79160456789', '41 10 045678'),
('Анатолий', 'Андреев', '+79161567890', '42 01 156789'),
('Лариса', 'Макарова', '+79162678901', '42 02 267890'),
('Виктор', 'Никитин', '+79163789012', '42 03 378901'),
('Галина', 'Захарова', '+79164890123', '42 04 489012'),
('Борис', 'Зайцев', '+79165901234', '42 05 590123'),
('Валентина', 'Соловьева', '+79166012340', '42 06 601230'),
('Константин', 'Борисов', '+79167123401', '42 07 712340'),
('Маргарита', 'Яковлева', '+79168234012', '42 08 823401'),
('Георгий', 'Григорьев', '+79169340123', '42 09 934012'),
('Лидия', 'Романова', '+79160401234', '42 10 040123');


-- Заполнение таблицы booking (30 записей)
insert into booking (id_flight, id_place, id_passenger, booking_time, status) values
(1, 1, 1, '2024-01-15 10:30:00', true),
(1, 2, 2, '2024-01-15 11:45:00', true),
(2, 5, 3, '2024-01-16 09:20:00', true),
(2, 6, 4, '2024-01-16 14:15:00', true),
(3, 9, 5, '2024-01-17 08:45:00', true),
(3, 10, 6, '2024-01-17 12:30:00', true),
(4, 13, 7, '2024-01-18 16:20:00', true),
(4, 14, 8, '2024-01-18 18:45:00', true),
(5, 17, 9, '2024-01-19 07:15:00', true),
(5, 18, 10, '2024-01-19 09:40:00', true),
(6, 21, 11, '2024-01-20 11:25:00', true),
(6, 22, 12, '2024-01-20 13:50:00', true),
(7, 25, 13, '2024-01-21 15:35:00', true),
(7, 26, 14, '2024-01-21 17:10:00', true),
(8, 29, 15, '2024-01-22 19:45:00', true),
(8, 30, 16, '2024-01-22 21:20:00', true),
(9, 33, 17, '2024-01-23 08:05:00', true),
(9, 34, 18, '2024-01-23 10:30:00', true),
(10, 37, 19, '2024-01-24 12:15:00', true),
(10, 38, 20, '2024-01-24 14:40:00', true),
(11, 41, 21, '2024-01-25 16:25:00', true),
(11, 42, 22, '2024-01-25 18:50:00', true),
(12, 45, 23, '2024-01-26 20:15:00', true),
(12, 46, 24, '2024-01-26 22:40:00', true),
(13, 49, 25, '2024-01-27 07:55:00', true),
(13, 50, 26, '2024-01-27 09:20:00', true),
(14, 53, 27, '2024-01-28 11:45:00', true),
(14, 54, 28, '2024-01-28 13:10:00', true),
(15, 57, 29, '2024-01-29 15:35:00', true),
(15, 58, 30, '2024-01-29 17:00:00', true);

