****README in progress

# Process

## Importing Data

## Cleaning Data

### Normalizing capitalization
```sql
# Normalize city names by making them all capitalized
update records
set city = upper(city);
```

### Identifying city naming inconsistencies
```sql
# Select distinct city names to see if there are any misspellings or inconsistencies
select distinct city
from records
order by city;
```

#### Updating inconsistencies
```sql
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
```

### Checking for Duplicates
```sql
# Search the table for any duplicate entries
## There shouldn't be multiple violation_record_id's for a single business, or they may have gotten double penalized for a single violation
select name, violation_record_id, count(*)
from records
where violation_record_id is not null
group by name, violation_record_id
having count(*) > 1;
```

### Checking for Missing Values
```sql
# Search table for relevant null fields
select name, address, description, city, zip_code, phone, business_id
from records
where address is null
or description is null
or phone is null
or city is null
or zip_code is null
or business_id is null
limit 5;
```
Result:

| name                             | address                        | description                        | city       | zip_code | phone | business_id |
|----------------------------------|--------------------------------|------------------------------------|------------|----------|-------|-------------|
| 4 POINTS SHERATON BISTRO KITCHEN | 22406 PACIFIC HWY S            | Seating 51-150 - Risk Category III | DES MOINES | 98198    |       | PR0085547   |
| 4 POINTS SHERATON BISTRO KITCHEN | 22406 PACIFIC HWY S            | Seating 51-150 - Risk Category III | DES MOINES | 98198    |       | PR0085547   |
| 4 POINTS SHERATON BISTRO KITCHEN | 22406 PACIFIC HWY S            | Seating 51-150 - Risk Category III | DES MOINES | 98198    |       | PR0085547   |
| 4 POINTS SHERATON BISTRO KITCHEN | 22406 PACIFIC HWY S            | Seating 51-150 - Risk Category III | DES MOINES | 98198    |       | PR0085547   |
| 4 POINTS SHERATON BISTRO KITCHEN | 22406 PACIFIC HWY S            | Seating 51-150 - Risk Category III | DES MOINES | 98198    |       | PR0085547   |

#### Identifying which columns have nulls
Could have done a count of nulls, but found out the only column with nulls was the `phone` column immediately.

```sql
# Remove phone from null field search and see if anything is returned
select name, address, description, city, zip_code, phone, business_id
from records
where address is null
or description is null
or city is null
or zip_code is null
or business_id is null;
```
Result: 

| name                             | address                        | description                        | city       | zip_code | phone | business_id |
|----------------------------------|--------------------------------|------------------------------------|------------|----------|-------|-------------|
| |          | |   |     |       |    |

#### TODO: Use python to scrape and iteratively fill missing phone numbers using name and address with google search

### Create `businesses` table to store business information independently

```sql
# Create table of business names, description, address, city, zip, phone, lon, lat, business_id, grade
create table businesses(
    id varchar(255),
    name varchar(255),
    program_identifier varchar(255),
    description varchar(255),
    grade varchar(5),
    address varchar(255),
    city varchar (255),
    zip varchar(25),
    phone varchar(25),
    longitude double,
    latitude double,
    inspection_business_name varchar(255)
);
```

### Populate businesses table 
```sql
insert into businesses
    select distinct
                    business_id,
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
```

### Check for missed duplicates in `businesses`
```sql
# Check for duplicate business names, id
select name, id, count(*)
from businesses
group by name, id
having count(*) > 1;
```

### Add missing `violations_id` column to main table
```sql
# Add violation_id column to main records table
alter table records
add column violation_id int;
```

#### Populate the column
Some of the descriptions already had the id's at the beginning

```sql
select violation_description
from records
where violation_description is not null
limit 5;
```

|violation_description           |
|--------------------------------|
|3300 - Potential food contamination prevented during delivery,  preparation, storage, display|
|0200 - Food Worker Cards current for all food workers; new food workers trained|
|0600 - Adequate handwashing facilities|
|2300 - Proper Consumer Advisory posted for raw ...|
|0200 - Food Worker Cards current for all food workers; new food workers trained|


Test query to make sure I'm pulling the right data
```sql
# Populate violation_id column from first 4 digits of violation_description
## Using regex, pull first 4 digits of violation_description where the description begins with a number
select name, left(violation_description, 4)
from records
where regexp_like(violation_description, '^[0-9]');
```

|name                            |violation_description                                                                        |left(violation_description, 4)|
|--------------------------------|---------------------------------------------------------------------------------------------|------------------------------|
|100 LB CLAM                     |3300 - Potential food contamination prevented during delivery,  preparation, storage, display|3300                          |
|100 LB CLAM                     |0200 - Food Worker Cards current for all food workers; new food workers trained              |0200                          |
|100 LB CLAM                     |0600 - Adequate handwashing facilities                                                       |0600                          |
|100 LB CLAM                     |2300 - Proper Consumer Advisory posted for raw ...                                           |2300                          |


Turn above query into an update query to fill `violations_id` column
```sql
update records
set records.violation_id = left(violation_description, 4)
where regexp_like(violation_description, '^[0-9]');
```

Not all rows had the violation id's in the description, however. Try matching `violation_description` to `description` from the `violation_codes` table:
```sql
# Find rows that did not have the violation_id in the violation_description and find the corresponding id's using a partial string join
select distinct violation_description, id
from records r
    join violation_codes vc on left(r.violation_description, 20) = left(vc.description, 20)
where violation_description is not null
and violation_id is null;
```
|violation_description           |id                                                                                           |
|--------------------------------|---------------------------------------------------------------------------------------------|
|Warewashing facilities properly installed,...|4100                                                                                         |
|Wiping cloths properly used, stored|3400                                                                                         |
|Proper cold holding temperatures (greater than  45 degrees F)|2120                                                                                         |
|Proper cold holding temperatures (greater than  45 degrees F)|2110                                                                                         |

Query works, inspected for accuracy manually since there aren't too many codes. Updating step: 
```sql
# Fill these values using matching from above query
## Inefficient but simple
update records r, violation_codes vc
set r.violation_id = vc.id
where left(r.violation_description, 20) = left(vc.description, 20)
and violation_id is null;
```

Double check if id's are filled correctly
```sql
# Manually check if id's are correct
select distinct violation_id, violation_description
from records
```

|violation_id                    |violation_description                                                                        |
|--------------------------------|---------------------------------------------------------------------------------------------|
|                                |                                                                                             |
|3300                            |3300 - Potential food contamination prevented during delivery,  preparation, storage, display|
|200                             |0200 - Food Worker Cards current for all food workers; new food workers trained              |
|600                             |0600 - Adequate handwashing facilities                                                       |


### Creating `inspection_records`
```sql
create table inspection_records(
    id varchar(255),
    `date` date,
    business_id varchar(255),
    violation_record_id varchar(255),
    violation_id int,
    type varchar(255),
    score int,
    result varchar(25),
    closed_business bool
);
```

```sql
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
    from records
```

|id                              |date                                                                                         |business_id|violation_record_id|violation_id|type                           |score|result      |closed_business|
|--------------------------------|---------------------------------------------------------------------------------------------|-----------|-------------------|------------|-------------------------------|-----|------------|---------------|
|DAWWGK08K                       |2022-01-13                                                                                   |PR0089260  |                   |            |Routine Inspection/Field Review|0    |Satisfactory|0              |
|DAUHM2FT8                       |2021-01-06                                                                                   |PR0089260  |                   |            |Routine Inspection/Field Review|0    |Satisfactory|0              |
|DAZLMUFYH                       |2021-12-29                                                                                   |PR0046367  |                   |            |Routine Inspection/Field Review|0    |Satisfactory|0              |
|DAZMP7KTI                       |2020-07-29                                                                                   |PR0046367  |                   |            |Consultation/Education - Field |0    |Satisfactory|0              |
|                                |                                                                                             |PR0090156  |                   |            |                               |     |            |               |

Now, we can join businesses to inspection records using the id
```sql
select distinct name, result
from inspection_records
join businesses b on inspection_records.business_id = b.id
limit 5;
```
|name                            |result                                                                                       |
|--------------------------------|---------------------------------------------------------------------------------------------|
|#807 TUTTA BELLA                |Satisfactory                                                                                 |
|+MAS CAFE                       |Satisfactory                                                                                 |
|?al?al Cafe                     |                                                                                             |
|100 LB CLAM                     |Incomplete                                                                                   |
|100 LB CLAM                     |Unsatisfactory                                                                               |
