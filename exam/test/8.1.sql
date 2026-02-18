CREATE TABLE IF NOT EXISTS customers (
    id serial PRIMARY KEY,
    name VARCHAR(100) not null,
    email VARCHAR(100) not null UNIQUE
);
create table if not exists products (
    id serial primary key,
    name VARCHAR(100) not null,
    price DECIMAL(10, 2) not null
);
create table if not exists orders (
    id serial PRIMARY KEY,
    customer_id integer not null REFERENCES customers(id),
    total_amount DECIMAL(10, 2) not null,
    date DATE not null
);
create table if not exists order_items (
    id serial PRIMARY KEY,
    order_id integer not null REFERENCES orders(id),
    product_id integer not null REFERENCES products(id),
    price DECIMAL(10, 2) not null,
    quantity INTEGER not null
);
insert into
    customers (name, email)
values
    ('ivan', 'ivan@gmail.com'),
    ('maria', 'maria@mail.ru'),
    ('alex', 'alex@yandex.ru'),
    ('olga', 'olga@gmail.com'),
    ('dmitry', 'dmitry@mail.ru');
insert into
    customers (id, name, email)
values
    (2, 'steph', 'steph@gmail.com');
select
    *
from
    customers;
insert into
    products (name, price)
values
    ('laptop', 89999.00),
    ('mouse', 1500.00),
    ('keyboard', 4500.00),
    ('monitor', 25000.00),
    ('headphones', 3500.00),
    ('webcam', 7200.00);
insert into
    orders (customer_id, total_amount, date)
values
    (1, 95000.00, '2024-01-15'),
    (1, 6000.00, '2024-02-20'),
    (2, 120000.00, '2024-03-10'),
    (2, 8500.00, '2024-04-05'),
    (3, 3500.00, '2024-05-12'),
    (4, 110000.00, '2024-06-01'),
    (5, 2000.00, '2024-07-08');
insert into
    order_items (order_id, product_id, price, quantity)
values
    (22, 1, 89999.00, 1),
    (22, 2, 1500.00, 1),
    (24, 2, 1500.00, 2),
    (24, 3, 4500.00, 1),
    (25, 1, 89999.00, 1),
    (25, 4, 25000.00, 1),
    (26, 3, 4500.00, 1),
    (26, 5, 3500.00, 1),
    (27, 5, 3500.00, 1),
    (28, 1, 89999.00, 1),
    (28, 4, 25000.00, 1);
select
    o. *
from
    orders o
where
    o.customer_id in (
        select
            customer_id
        from
            orders
        group by
            customer_id
        having
            sum(total_amount) > 20000
    );
SELECT
    rank() over (
        order by
            sum(total_amount) over (PARTITION BY customer_id) desc
    )
from
    orders;
EXPLAIN ANALYSE(
    with customer_total as (
        select
            customer_id,
            sum(total_amount) as total
        from
            orders
        group by
            customer_id
    )
    select
        rank() over (
            ORDER BY
                customer_total.total desc
        ),
        customer_total.total
    from
        customer_total
    group by
        customer_total.total
);
create index idx_order_customer_id on orders(customer_id);
create index idx_order_date on orders(date);