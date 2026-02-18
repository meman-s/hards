CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department_id INTEGER,
    salary DECIMAL(10, 2),
    hire_date DATE
);
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);
insert into
    departments (name)
values
    ('Разрабы'),
    ('Аналы'),
    ('Руки'),
    ('1с-ники');
insert into
    employees (name, department_id, salary, hire_date)
VALUES
    ('ivan', 1, 180000, '2023-02-14'),
    ('maria', 2, 150000, '2022-09-01'),
    ('alex', 2, 130000, '2024-03-20'),
    ('olga', 3, 90000, '2021-06-10'),
    ('dmitry', 4, 140000, '2020-12-03'),
    ('anna', 1, 210000, '2024-01-08'),
    ('pavel', 3, 95000, '2023-07-29');
select
    e. *
from
    employees e
where
    e.salary > (
        select
            avg(salary)
        from
            employees
        WHERE
            e.department_id = department_id
    );
EXPLAIN ANALYSE (
    select
        id,
        name,
        department_id,
        salary,
        hire_date,
        sum(salary) over (
            PARTITION BY department_id
            ORDER BY
                hire_date
        )
    from
        employees
    order by
        department_id,
        hire_date
);
create index idx_dep_salary on employees(department_id, salary);
create index idx_dep_hires on employees(hire_date, department_id);
create index idx_dep_hir on employees(hire_date);
create index idx_dep_hi on employees(department_id);
create table if not exists stats (
    id serial primary key,
    department_id integer not null references departments(id),
    amount integer
);
insert into
    stats (department_id, amount)
VALUES
    (1, 3),
    (2, 2),
    (3, 2),
    (4, 1);
create
or REPLACE function update_stats() returns trigger as $$ BEGIN
    if TG_OP = 'INSERT' THEN
    update
        stats
    set
        amount = amount + 1
    where
        department_id = NEW .department_id;
return new;
else
update
    stats
set
    amount = amount - 1
where
    department_id = OLD .department_id;
end if;
return old;
RETURN NULL;
END;
$$ LANGUAGE plpgsql;
create
or replace TRIGGER stats_update after
insert
    or
delete
    on employees for each row EXECUTE function update_stats();
delete from
    employees
where
    id = 11;