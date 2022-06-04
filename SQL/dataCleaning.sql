# Normalize city names by making them all capital
update records
set city = upper(city);

# Select distinct city names to see if there are any misspellings or inconsistencies
select distinct city
from records
order by city;

# Set all 'SEA TAC' entries to 'SEATAC'
update records
set city = 'SEATAC'
where city = 'SEA TAC';

# Set all 'VASHON ISLAND' city names to 'VASHON'
update records
set city = 'VASHON'
where city = 'VASHON ISLAND';

# Set 'WEST SEATTLE' city names to 'SEATTLE'
update records
set city = 'SEATTLE'
where city = 'WEST SEATTLE';

# Search the table for any duplicate entries
## There shouldn't be multiple violation_record_id's for a single business, or they may have gotten double penalized for a single violation
select name, violation_record_id, count(*)
from records
where violation_record_id is not null
group by name, violation_record_id
having count(*) > 1;

# Search table for relevant null fields
## Only null phone numbers were present
select name, address, description, city, zip_code, phone, business_id
from records
where address is null
   or description is null
   or city is null
   or zip_code is null
   or business_id is null;

# TODO: Use python to scrape and iteratively fill missing phone numbers using name and address with google search

# Create table for violation code reference
create table violation_codes
(
    id          int,
    description varchar(255),
    points      smallint,
    color_code  varchar(30)
);

# Create table of business names, description, address, city, zip, phone, lon, lat, business_id, grade
create table businesses
(
    id                       varchar(255),
    name                     varchar(255),
    program_identifier       varchar(255),
    description              varchar(255),
    grade                    varchar(5),
    address                  varchar(255),
    city                     varchar(255),
    zip                      varchar(25),
    phone                    varchar(25),
    longitude                double,
    latitude                 double,
    inspection_business_name varchar(255)
);

insert into businesses
select distinct business_id,
                name,
                program_identifier,
                description,
                grade,
                address,
                city,
                zip_code,
                phone,
                longitude,
                latitude,
                inspection_business_name
from records;

# Check for duplicate business names, id
select name, id, count(*)
from businesses
group by name, id
having count(*) > 1;

# Add violation_id column to main records table
alter table records
    add column violation_id int;

select violation_description
from records
where violation_description is not null;

# Populate violation_id column from first 4 digits of violation_description
## Using regex, pull first 4 digits of violation_description where the description begins with a number
select name, violation_description, left(violation_description, 4)
from records
where regexp_like(violation_description, '^[0-9]');

update records
set records.violation_id = left(violation_description, 4)
where regexp_like(violation_description, '^[0-9]');

# Find rows that did not have the violation_id in the violation_description and find the corresponding id's using a partial string join
select distinct violation_description, id
from records r
         join violation_codes vc on left(r.violation_description, 20) = left(vc.description, 20)
where violation_description is not null
  and violation_id is null;

# Fill these values using matching from above query
## Inefficient but simple
update records r, violation_codes vc
set r.violation_id = vc.id
where left(r.violation_description, 20) = left(vc.description, 20)
  and violation_id is null;

# Manually check if id's are correct
select distinct violation_id, violation_description
from records

create table inspection_records
(
    id                  varchar(255),
    `date`              date,
    business_id         varchar(255),
    violation_record_id varchar(255),
    violation_id        int,
    type                varchar(255),
    score               int,
    result              varchar(25),
    closed_business     bool
);

insert into inspection_records
select inspection_serial_num,
       inspection_date,
       business_id,
       violation_record_id,
       violation_id,
       inspection_type,
       inspection_score,
       inspection_result,
       inspection_closed_business
from records;

select distinct name, result
from inspection_records
         join businesses b on inspection_records.business_id = b.id
limit 5;

# Drop null records
delete
from inspection_records
where id is null;

select id, count(*)
from inspection_records
group by id
having count(*) > 1;

# Add relationships for new tables
alter table violation_codes
    add constraint primary key (id);

alter table businesses
    add constraint primary key (id);

alter table inspection_records
    add foreign key (violation_id) references violation_codes (id)

# Add phone numbers using python
select distinct name, address, city
from records
where phone is null
