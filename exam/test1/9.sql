create table if not exists sales (
    id serial primary key,
    product_id integer not null,
    amount decimal(10,2) not null,
    sale_date date not null
);

select * from sales;

select
    sum(amount) over (partition by sale_date)
from sales;

select
    rank() over (partition by sale_date order by amount desc)
from sales;
