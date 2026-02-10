-- ============================================
-- SQL ЗАДАЧИ ДЛЯ ПРАКТИКИ
-- ============================================

-- ============================================
-- СТРУКТУРА ТАБЛИЦ
-- ============================================

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    registration_date DATE
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    product_price DECIMAL(10,2),
    category VARCHAR(50)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE,
    status VARCHAR(20)
);

CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT
);

-- ============================================
-- ТЕСТОВЫЕ ДАННЫЕ
-- ============================================

INSERT INTO customers VALUES
(1, 'Иван Иванов', 'ivan@mail.ru', '2023-01-15'),
(2, 'Петр Петров', 'petr@mail.ru', '2023-02-20'),
(3, 'Мария Сидорова', 'maria@mail.ru', '2023-03-10'),
(4, 'Анна Козлова', 'anna@mail.ru', '2024-01-05'),
(5, 'Дмитрий Смирнов', 'dmitry@mail.ru', '2024-02-12');

INSERT INTO products VALUES
(1, 'Ноутбук', 50000.00, 'Электроника'),
(2, 'Мышь', 1000.00, 'Электроника'),
(3, 'Клавиатура', 2500.00, 'Электроника'),
(4, 'Стол', 8000.00, 'Мебель'),
(5, 'Стул', 5000.00, 'Мебель');

INSERT INTO orders VALUES
(1, 1, '2024-01-15', 'completed'),
(2, 1, '2024-01-20', 'completed'),
(3, 2, '2024-01-25', 'completed'),
(4, 3, '2024-02-01', 'completed'),
(5, 1, '2024-02-10', 'pending'),
(6, 4, '2024-02-15', 'completed'),
(7, 2, '2024-02-20', 'cancelled');

INSERT INTO order_items VALUES
(1, 1, 1, 1),  -- заказ 1: 1 ноутбук
(2, 1, 2, 2),  -- заказ 1: 2 мыши
(3, 2, 3, 1),  -- заказ 2: 1 клавиатура
(4, 3, 1, 1),  -- заказ 3: 1 ноутбук
(5, 3, 2, 1),  -- заказ 3: 1 мышь
(6, 4, 4, 1),  -- заказ 4: 1 стол
(7, 4, 5, 2),  -- заказ 4: 2 стула
(8, 5, 3, 1),  -- заказ 5: 1 клавиатура
(9, 6, 1, 1),  -- заказ 6: 1 ноутбук
(10, 6, 3, 1), -- заказ 6: 1 клавиатура
(11, 7, 2, 3); -- заказ 7: 3 мыши (отменен)

-- ============================================
-- ЗАДАЧИ
-- ============================================

-- ЗАДАЧА 1: Подсчет заказов
-- Напишите запрос, который выведет имя каждого клиента и количество его заказов.
-- Клиенты без заказов тоже должны быть в результате (с количеством 0).
-- 
-- Ожидаемый результат:
-- customer_name | order_count
-- Иван Иванов  | 3
-- Петр Петров  | 2
-- Мария Сидорова | 1
-- Анна Козлова | 1
-- Дмитрий Смирнов | 0

-- ВАШ ЗАПРОС ЗДЕСЬ:

-- Вариант 1 (с подзапросом) - ИСПРАВЛЕНО:
SELECT 
    customer_name,
    (SELECT COUNT(*) FROM orders WHERE customer_id = c.customer_id) as order_count
FROM customers c;

-- Вариант 2 (с JOIN) - ИСПРАВЛЕНО: нужно LEFT JOIN вместо JOIN
SELECT
    c.customer_name,
    COALESCE(COUNT(o.order_id), 0) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY order_count DESC;




-- ============================================

-- ЗАДАЧА 2: Выручка по категориям
-- Напишите запрос, который выведет категорию продукта и общую выручку по этой категории.
-- Выручка = сумма (цена * количество) для всех проданных продуктов этой категории.
-- Учитывайте только завершенные заказы (status = 'completed').
-- Результат отсортируйте по выручке по убыванию.
--
-- Ожидаемый результат:
-- category      | total_revenue
-- Электроника  | 111500.00
-- Мебель        | 18000.00

-- ВАШ ЗАПРОС ЗДЕСЬ:

-- ИСПРАВЛЕНО: убрал product_id из GROUP BY (группируем только по category)
SELECT
    p.category,
    SUM(oi.quantity * p.product_price) as total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY p.category
ORDER BY total_revenue DESC;



-- ============================================

-- ЗАДАЧА 3: Клиенты с большими заказами
-- Напишите запрос, который выведет имена клиентов, у которых общая сумма всех заказов
-- превышает 50000 рублей.
-- Учитывайте только завершенные заказы (status = 'completed').
-- Результат отсортируйте по сумме заказов по убыванию.
--
-- Ожидаемый результат:
-- customer_name | total_spent
-- Иван Иванов  | 53000.00
-- Петр Петров  | 51000.00
-- Анна Козлова | 52500.00

-- ВАШ ЗАПРОС ЗДЕСЬ:

with customer_totals as (
    select
        customer_id,
        customer_name,
        sum(oi.quantity * p.product_price) over (PARTITION by customer_id) as total_spent
    from customers c
    join orders o on c.customer_id = o.customer_id
    join order_items oi on o.order_id = oi.order_id
    join products p on oi.product_id = p.product_id
    where o.status = 'completed'
)

SELECT DISTINCT
    customer_name,
    total_spent
from customer_totals
where total_spent > 50000
order by total_spent DESC



select
    customer_name,
    sum(oi.quantity * p.product_id) as total_spent
from customers c
join orders o on c.customer_id = o.customer_id
join order_items oi on o.order_id = oi.order_id
join products p on oi.product_id = p.product_id
where o.status = 'completed'
group by customer_name, customer_id
having sum(oi.quantity * p.product_id) > 50000
order by total_spent DESC



-- ============================================
-- РЕШЕНИЯ (для проверки)
-- ============================================

-- РЕШЕНИЕ ЗАДАЧИ 1:
-- SELECT 
--     c.customer_name,
--     COALESCE(COUNT(o.order_id), 0) as order_count
-- FROM customers c
-- LEFT JOIN orders o ON c.customer_id = o.customer_id
-- GROUP BY c.customer_id, c.customer_name
-- ORDER BY order_count DESC;

-- РЕШЕНИЕ ЗАДАЧИ 2:
-- SELECT 
--     p.category,
--     SUM(oi.quantity * p.product_price) as total_revenue
-- FROM products p
-- JOIN order_items oi ON p.product_id = oi.product_id
-- JOIN orders o ON oi.order_id = o.order_id
-- WHERE o.status = 'completed'
-- GROUP BY p.category
-- ORDER BY total_revenue DESC;

-- РЕШЕНИЕ ЗАДАЧИ 3:
-- SELECT 
--     c.customer_name,
--     SUM(oi.quantity * p.product_price) as total_spent
-- FROM customers c
-- JOIN orders o ON c.customer_id = o.customer_id
-- JOIN order_items oi ON o.order_id = oi.order_id
-- JOIN products p ON oi.product_id = p.product_id
-- WHERE o.status = 'completed'
-- GROUP BY c.customer_id, c.customer_name
-- HAVING SUM(oi.quantity * p.product_price) > 50000
-- ORDER BY total_spent DESC;
