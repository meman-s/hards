-- ============================================
-- SQL ПРАКТИКА: Примеры и объяснения
-- ============================================

-- ============================================
-- КРАТКИЙ СПРАВОЧНИК
-- ============================================

-- ============================================
-- ТИПЫ JOIN (Соединения таблиц)
-- ============================================

-- INNER JOIN (Внутреннее соединение)
-- Возвращает только строки, где есть совпадение в обеих таблицах
-- Синтаксис: FROM table1 INNER JOIN table2 ON table1.id = table2.id
-- Или просто: FROM table1 JOIN table2 ON table1.id = table2.id
-- Пример: SELECT * FROM customers c JOIN orders o ON c.id = o.customer_id
-- Результат: Только клиенты с заказами

-- LEFT JOIN (Левое внешнее соединение)
-- Возвращает все строки из левой таблицы + совпадения из правой
-- Если совпадения нет, поля правой таблицы = NULL
-- Синтаксис: FROM table1 LEFT JOIN table2 ON table1.id = table2.id
-- Пример: SELECT * FROM customers c LEFT JOIN orders o ON c.id = o.customer_id
-- Результат: Все клиенты, даже без заказов (заказы = NULL)

-- RIGHT JOIN (Правое внешнее соединение)
-- Возвращает все строки из правой таблицы + совпадения из левой
-- Если совпадения нет, поля левой таблицы = NULL
-- Синтаксис: FROM table1 RIGHT JOIN table2 ON table1.id = table2.id
-- Пример: SELECT * FROM customers c RIGHT JOIN orders o ON c.id = o.customer_id
-- Результат: Все заказы, даже без клиентов (клиенты = NULL)
-- ВАЖНО: RIGHT JOIN редко используется, обычно заменяется на LEFT JOIN

-- FULL OUTER JOIN (Полное внешнее соединение)
-- Возвращает все строки из обеих таблиц
-- Если совпадения нет, поля другой таблицы = NULL
-- Синтаксис: FROM table1 FULL OUTER JOIN table2 ON table1.id = table2.id
-- Пример: SELECT * FROM customers c FULL OUTER JOIN orders o ON c.id = o.customer_id
-- Результат: Все клиенты И все заказы

-- CROSS JOIN (Декартово произведение)
-- Возвращает все возможные комбинации строк из обеих таблиц
-- Синтаксис: FROM table1 CROSS JOIN table2
-- Или: FROM table1, table2 (старый синтаксис)
-- Пример: SELECT * FROM customers CROSS JOIN products
-- Результат: Каждый клиент × каждый продукт (может быть очень много строк!)
-- ВАЖНО: Используйте осторожно, может вернуть миллионы строк

-- SELF JOIN (Самообъединение)
-- Соединение таблицы с самой собой
-- Пример: Найти сотрудников и их менеджеров
-- SELECT e.name, m.name as manager
-- FROM employees e
-- LEFT JOIN employees m ON e.manager_id = m.id

-- Сравнение JOIN:
-- INNER JOIN: только совпадения (A ∩ B)
-- LEFT JOIN: все из A + совпадения (A ∪ (A ∩ B))
-- RIGHT JOIN: все из B + совпадения (B ∪ (A ∩ B))
-- FULL JOIN: все из A и B (A ∪ B)
-- CROSS JOIN: все комбинации (A × B)

-- ============================================
-- АГРЕГАТНЫЕ ФУНКЦИИ
-- ============================================

-- COUNT() - подсчет строк
-- COUNT(*) - все строки (включая NULL)
-- COUNT(column) - строки, где column не NULL
-- COUNT(DISTINCT column) - уникальные значения
-- Пример: SELECT COUNT(*) FROM orders; -- всего заказов
-- Пример: SELECT COUNT(DISTINCT customer_id) FROM orders; -- уникальных клиентов

-- SUM() - сумма значений
-- Пример: SELECT SUM(price) FROM products;
-- Работает только с числовыми типами

-- AVG() - среднее значение
-- Пример: SELECT AVG(price) FROM products;
-- Игнорирует NULL значения

-- MIN() - минимальное значение
-- Пример: SELECT MIN(price) FROM products;
-- Работает с числами, датами, строками

-- MAX() - максимальное значение
-- Пример: SELECT MAX(price) FROM products;
-- Работает с числами, датами, строками

-- STRING_AGG() / GROUP_CONCAT() - объединение строк
-- PostgreSQL: SELECT STRING_AGG(name, ', ') FROM products;
-- MySQL: SELECT GROUP_CONCAT(name SEPARATOR ', ') FROM products;
-- Пример: 'Ноутбук, Мышь, Клавиатура'

-- ARRAY_AGG() - массив значений (PostgreSQL)
-- Пример: SELECT ARRAY_AGG(name) FROM products;
-- Результат: {'Ноутбук', 'Мышь', 'Клавиатура'}

-- ============================================
-- СТРОКОВЫЕ ФУНКЦИИ
-- ============================================

-- CONCAT() - объединение строк
-- Пример: SELECT CONCAT(first_name, ' ', last_name) as full_name;
-- PostgreSQL: SELECT first_name || ' ' || last_name; (оператор ||)

-- LENGTH() / LEN() - длина строки
-- Пример: SELECT LENGTH('Hello'); -- 5

-- UPPER() - верхний регистр
-- Пример: SELECT UPPER('hello'); -- 'HELLO'

-- LOWER() - нижний регистр
-- Пример: SELECT LOWER('HELLO'); -- 'hello'

-- TRIM() - удаление пробелов
-- TRIM(LEADING ' ' FROM str) - слева
-- TRIM(TRAILING ' ' FROM str) - справа
-- TRIM(BOTH ' ' FROM str) - с обеих сторон
-- Пример: SELECT TRIM('  hello  '); -- 'hello'

-- SUBSTRING() / SUBSTR() - подстрока
-- Пример: SELECT SUBSTRING('Hello', 1, 3); -- 'Hel'
-- PostgreSQL: SELECT SUBSTRING('Hello' FROM 1 FOR 3);

-- REPLACE() - замена подстроки
-- Пример: SELECT REPLACE('Hello', 'l', 'L'); -- 'HeLLo'

-- POSITION() / CHARINDEX() - позиция подстроки
-- PostgreSQL: SELECT POSITION('ll' IN 'Hello'); -- 3
-- SQL Server: SELECT CHARINDEX('ll', 'Hello'); -- 3

-- LIKE - поиск по шаблону
-- % - любое количество символов
-- _ - один символ
-- Пример: SELECT * FROM customers WHERE name LIKE 'Иван%';
-- Пример: SELECT * FROM customers WHERE email LIKE '%@gmail.com';

-- ILIKE - LIKE без учета регистра (PostgreSQL)
-- Пример: SELECT * FROM customers WHERE name ILIKE 'иван%';

-- ============================================
-- ФУНКЦИИ ДАТЫ И ВРЕМЕНИ
-- ============================================

-- CURRENT_DATE - текущая дата
-- Пример: SELECT CURRENT_DATE; -- '2024-01-15'

-- CURRENT_TIMESTAMP / NOW() - текущая дата и время
-- Пример: SELECT NOW(); -- '2024-01-15 10:30:45'

-- DATE_TRUNC() - обрезка даты (PostgreSQL)
-- Пример: SELECT DATE_TRUNC('month', order_date); -- начало месяца
-- Пример: SELECT DATE_TRUNC('year', order_date); -- начало года
-- Варианты: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute'

-- EXTRACT() - извлечение части даты
-- Пример: SELECT EXTRACT(YEAR FROM order_date); -- 2024
-- Пример: SELECT EXTRACT(MONTH FROM order_date); -- 1
-- Варианты: YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, DOW (день недели)

-- AGE() - разница между датами (PostgreSQL)
-- Пример: SELECT AGE('2024-01-15', '2020-01-01'); -- '4 years 0 mons 14 days'

-- DATEDIFF() - разница между датами (MySQL, SQL Server)
-- MySQL: SELECT DATEDIFF('2024-01-15', '2020-01-01'); -- 1445 дней
-- SQL Server: SELECT DATEDIFF(day, '2020-01-01', '2024-01-15');

-- DATE_ADD() / DATE_SUB() - добавление/вычитание интервала
-- MySQL: SELECT DATE_ADD('2024-01-15', INTERVAL 1 MONTH);
-- PostgreSQL: SELECT '2024-01-15'::date + INTERVAL '1 month';

-- TO_CHAR() - форматирование даты (PostgreSQL)
-- Пример: SELECT TO_CHAR(order_date, 'DD.MM.YYYY'); -- '15.01.2024'

-- ============================================
-- ЧИСЛОВЫЕ ФУНКЦИИ
-- ============================================

-- ROUND() - округление
-- Пример: SELECT ROUND(3.14159, 2); -- 3.14
-- Пример: SELECT ROUND(3.5); -- 4

-- FLOOR() - округление вниз
-- Пример: SELECT FLOOR(3.7); -- 3

-- CEIL() / CEILING() - округление вверх
-- Пример: SELECT CEIL(3.2); -- 4

-- ABS() - абсолютное значение
-- Пример: SELECT ABS(-5); -- 5

-- POWER() - возведение в степень
-- Пример: SELECT POWER(2, 3); -- 8

-- SQRT() - квадратный корень
-- Пример: SELECT SQRT(16); -- 4

-- MOD() / % - остаток от деления
-- Пример: SELECT MOD(10, 3); -- 1
-- Пример: SELECT 10 % 3; -- 1

-- RANDOM() / RAND() - случайное число
-- PostgreSQL: SELECT RANDOM(); -- 0.0 - 1.0
-- MySQL: SELECT RAND(); -- 0.0 - 1.0

-- ============================================
-- УСЛОВНЫЕ ФУНКЦИИ
-- ============================================

-- CASE - условная логика
-- Синтаксис 1 (простое сравнение):
-- CASE column
--     WHEN value1 THEN result1
--     WHEN value2 THEN result2
--     ELSE result3
-- END

-- Синтаксис 2 (условия):
-- CASE
--     WHEN condition1 THEN result1
--     WHEN condition2 THEN result2
--     ELSE result3
-- END

-- Пример:
-- SELECT 
--     name,
--     CASE 
--         WHEN price > 1000 THEN 'Дорогой'
--         WHEN price > 100 THEN 'Средний'
--         ELSE 'Дешевый'
--     END as price_category
-- FROM products;

-- COALESCE() - первое не-NULL значение
-- Пример: SELECT COALESCE(NULL, NULL, 'Hello'); -- 'Hello'
-- Пример: SELECT COALESCE(phone, email, 'Нет контакта'); -- первый не-NULL

-- NULLIF() - возвращает NULL, если значения равны
-- Пример: SELECT NULLIF(5, 5); -- NULL
-- Пример: SELECT NULLIF(5, 3); -- 5

-- IFNULL() / ISNULL() - замена NULL (MySQL, SQL Server)
-- MySQL: SELECT IFNULL(phone, 'Нет телефона');
-- SQL Server: SELECT ISNULL(phone, 'Нет телефона');
-- PostgreSQL: SELECT COALESCE(phone, 'Нет телефона');

-- GREATEST() - наибольшее значение (PostgreSQL)
-- Пример: SELECT GREATEST(1, 5, 3); -- 5

-- LEAST() - наименьшее значение (PostgreSQL)
-- Пример: SELECT LEAST(1, 5, 3); -- 1

-- ============================================
-- ОПЕРАТОРЫ
-- ============================================

-- Арифметические: +, -, *, /, %, ^ (степень)
-- Сравнения: =, !=, <>, <, >, <=, >=
-- Логические: AND, OR, NOT
-- Проверка NULL: IS NULL, IS NOT NULL
-- Диапазон: BETWEEN value1 AND value2 (включая границы)
-- Список: IN (value1, value2, ...), NOT IN
-- Подстрока: LIKE, ILIKE (PostgreSQL)
-- Регулярные выражения: ~ (PostgreSQL), REGEXP (MySQL)

-- ============================================
-- ОСНОВНЫЕ ТИПЫ ДАННЫХ
-- ============================================

-- Числовые:
-- INTEGER / INT - целое число (-2^31 до 2^31-1)
-- BIGINT - большое целое (-2^63 до 2^63-1)
-- SMALLINT - маленькое целое (-32768 до 32767)
-- DECIMAL(p, s) / NUMERIC(p, s) - точное число (p - точность, s - масштаб)
-- REAL / FLOAT - число с плавающей точкой
-- DOUBLE PRECISION - двойная точность

-- Строковые:
-- VARCHAR(n) - строка переменной длины (до n символов)
-- CHAR(n) - строка фиксированной длины (n символов, дополняется пробелами)
-- TEXT - строка неограниченной длины

-- Дата и время:
-- DATE - дата (YYYY-MM-DD)
-- TIME - время (HH:MM:SS)
-- TIMESTAMP - дата и время (YYYY-MM-DD HH:MM:SS)
-- TIMESTAMP WITH TIME ZONE - дата и время с часовым поясом
-- INTERVAL - интервал времени

-- Логические:
-- BOOLEAN - TRUE, FALSE, NULL

-- Другие:
-- JSON / JSONB - JSON данные (PostgreSQL)
-- ARRAY - массив (PostgreSQL)
-- UUID - уникальный идентификатор

-- ============================================
-- ПОЛЕЗНЫЕ КОНСТРУКЦИИ
-- ============================================

-- DISTINCT - уникальные значения
-- Пример: SELECT DISTINCT customer_id FROM orders;

-- LIMIT / OFFSET - ограничение выборки
-- PostgreSQL, MySQL: SELECT * FROM orders LIMIT 10 OFFSET 20;
-- SQL Server: SELECT TOP 10 * FROM orders; (OFFSET через ORDER BY)

-- ORDER BY - сортировка
-- ASC - по возрастанию (по умолчанию)
-- DESC - по убыванию
-- NULLS FIRST / NULLS LAST - порядок NULL значений
-- Пример: SELECT * FROM orders ORDER BY order_date DESC NULLS LAST;

-- GROUP BY - группировка
-- Все неагрегированные колонки должны быть в GROUP BY
-- Пример: SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;

-- HAVING - фильтрация после GROUP BY
-- WHERE фильтрует строки ДО группировки
-- HAVING фильтрует группы ПОСЛЕ группировки
-- Пример: SELECT customer_id, COUNT(*) as cnt 
--         FROM orders 
--         GROUP BY customer_id 
--         HAVING COUNT(*) > 5;

-- UNION - объединение результатов (удаляет дубликаты)
-- UNION ALL - объединение (НЕ удаляет дубликаты, быстрее)
-- Пример: 
-- SELECT name FROM table1
-- UNION
-- SELECT name FROM table2;

-- INTERSECT - пересечение (общие строки)
-- Пример: SELECT id FROM table1 INTERSECT SELECT id FROM table2;

-- EXCEPT / MINUS - разность (строки из первой таблицы, которых нет во второй)
-- Пример: SELECT id FROM table1 EXCEPT SELECT id FROM table2;

-- WITH (CTE - Common Table Expression) - временные именованные запросы
-- Пример:
-- WITH recent_orders AS (
--     SELECT * FROM orders WHERE order_date >= '2024-01-01'
-- )
-- SELECT * FROM recent_orders;

-- ============================================
-- 1. НОРМАЛИЗАЦИЯ БАЗЫ ДАННЫХ
-- ============================================

-- ТЕОРИЯ:
-- Нормализация - процесс организации данных в реляционной БД для:
-- 1. Уменьшения избыточности данных
-- 2. Устранения аномалий вставки, обновления и удаления
-- 3. Улучшения целостности данных
-- 4. Оптимизации использования места

-- Основные нормальные формы:
-- 1NF (Первая нормальная форма):
--   - Каждая ячейка содержит атомарное (неделимое) значение
--   - Нет повторяющихся групп данных
--   - Каждая строка уникальна
--   Пример нарушения: колонка "телефоны" с несколькими номерами через запятую

-- 2NF (Вторая нормальная форма):
--   - Должна быть в 1NF
--   - Все неключевые атрибуты полностью зависят от первичного ключа
--   - Нет частичных зависимостей (когда атрибут зависит только от части составного ключа)
--   Пример нарушения: в таблице заказов хранится имя клиента (зависит только от customer_id, а не от order_id)

-- 3NF (Третья нормальная форма):
--   - Должна быть в 2NF
--   - Нет транзитивных зависимостей (когда неключевой атрибут зависит от другого неключевого атрибута)
--   Пример нарушения: в таблице заказов хранится город клиента (зависит от адреса, а не напрямую от заказа)

-- BCNF (Бойса-Кодда нормальная форма):
--   - Усиленная версия 3NF
--   - Каждая детерминанта (атрибут, определяющий другие) является потенциальным ключом

-- Плюсы нормализации:
--   + Уменьшение дублирования данных
--   + Легче обновлять данные (изменение в одном месте)
--   + Меньше места для хранения
--   + Лучшая целостность данных

-- Минусы нормализации:
--   - Больше JOIN'ов в запросах (может быть медленнее)
--   - Более сложная структура БД

-- ПРИМЕР 1.1: ДО нормализации (плохая структура)
-- Проблемы этой структуры:
-- 1. Дублирование данных: имя и email клиента повторяются для каждого заказа
-- 2. Аномалия обновления: при смене email нужно обновлять все строки
-- 3. Аномалия удаления: удаление заказа может потерять информацию о клиенте
-- 4. Аномалия вставки: нельзя добавить клиента без заказа
-- 5. Неточность: цена продукта хранится в заказе (может измениться)

CREATE TABLE bad_orders (
    order_id INT,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    product_name VARCHAR(100),
    product_price DECIMAL(10,2),
    quantity INT,
    order_date DATE
);

-- Пример данных в bad_orders:
-- order_id | customer_name | customer_email      | product_name | product_price | quantity | order_date
-- 1        | Иван Иванов  | ivan@mail.ru       | Ноутбук      | 50000.00      | 1        | 2024-01-15
-- 2        | Иван Иванов  | ivan@mail.ru       | Мышь         | 1000.00       | 2        | 2024-01-20
-- 3        | Петр Петров  | petr@mail.ru       | Ноутбук      | 50000.00      | 1        | 2024-01-25

-- ПРИМЕР 1.2: ПОСЛЕ нормализации (хорошая структура)
-- Преимущества:
-- 1. Данные о клиентах хранятся один раз
-- 2. Данные о продуктах хранятся один раз
-- 3. Легко обновлять информацию о клиенте/продукте
-- 4. Можно добавлять клиентов без заказов
-- 5. Цена продукта хранится в таблице products (актуальная)

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    product_price DECIMAL(10,2)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE
);

CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT
);

-- Пример данных после нормализации:
-- customers:
-- customer_id | customer_name | customer_email
-- 1           | Иван Иванов  | ivan@mail.ru
-- 2           | Петр Петров  | petr@mail.ru

-- products:
-- product_id | product_name | product_price
-- 1          | Ноутбук      | 50000.00
-- 2          | Мышь         | 1000.00

-- orders:
-- order_id | customer_id | order_date
-- 1        | 1           | 2024-01-15
-- 2        | 1           | 2024-01-20
-- 3        | 2           | 2024-01-25

-- order_items:
-- order_item_id | order_id | product_id | quantity
-- 1             | 1        | 1         | 1
-- 2             | 2        | 2         | 2
-- 3             | 3        | 1         | 1

-- ============================================
-- 2. ПОДЗАПРОСЫ (SUBQUERIES)
-- ============================================

-- ТЕОРИЯ:
-- Подзапрос (subquery) - это SELECT запрос, вложенный в другой SQL запрос
-- Подзапросы могут использоваться в: SELECT, FROM, WHERE, HAVING, INSERT, UPDATE, DELETE

-- Типы подзапросов:
-- 1. Некоррелированный (независимый):
--    - Выполняется один раз
--    - Не зависит от внешнего запроса
--    - Пример: WHERE id IN (SELECT id FROM table2)

-- 2. Коррелированный (зависимый):
--    - Выполняется для каждой строки внешнего запроса
--    - Использует значения из внешнего запроса
--    - Может быть медленным
--    - Пример: WHERE EXISTS (SELECT 1 FROM table2 WHERE table2.id = table1.id)

-- 3. Скалярный подзапрос:
--    - Возвращает одно значение (одна строка, одна колонка)
--    - Может использоваться везде, где ожидается значение

-- ПРИМЕР 2.1: Скалярный подзапрос в SELECT
-- Задача: Для каждого клиента показать количество его заказов
-- Пояснение: Подзапрос выполняется для каждой строки customers и возвращает COUNT(*)

SELECT 
    customer_name,
    (SELECT COUNT(*) FROM orders WHERE orders.customer_id = customers.customer_id) as order_count
FROM customers;

-- Ожидаемый результат:
-- customer_name | order_count
-- Иван Иванов  | 2
-- Петр Петров  | 1

-- ПРИМЕР 2.2: Подзапрос в WHERE с IN
-- Задача: Найти всех клиентов, которые делали заказы после 2024-01-01
-- Пояснение: IN проверяет, входит ли customer_id в список значений из подзапроса
-- ВАЖНО: Подзапрос должен возвращать одну колонку

SELECT customer_name
FROM customers
WHERE customer_id IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE order_date >= '2024-01-01'
);

-- Ожидаемый результат:
-- customer_name
-- Иван Иванов
-- Петр Петров

-- ПРИМЕР 2.3: Подзапрос с EXISTS
-- Задача: То же самое, но с EXISTS
-- Пояснение: EXISTS возвращает TRUE, если подзапрос вернул хотя бы одну строку
-- ПРЕИМУЩЕСТВО: EXISTS часто быстрее IN, т.к. останавливается при первом совпадении
-- ВАЖНО: В EXISTS обычно используется SELECT 1 (не SELECT *)

SELECT customer_name
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id 
    AND o.order_date >= '2024-01-01'
);

-- Ожидаемый результат:
-- customer_name
-- Иван Иванов
-- Петр Петров

-- ПРИМЕР 2.4: NOT EXISTS
-- Задача: Найти клиентов, которые НИ РАЗУ не делали заказы
-- Пояснение: NOT EXISTS возвращает TRUE, если подзапрос не вернул ни одной строки

SELECT customer_name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
);

-- Ожидаемый результат (если есть клиент без заказов):
-- customer_name
-- (пусто, если все клиенты делали заказы)

-- ПРИМЕР 2.5: Подзапрос в FROM (производная таблица)
-- Задача: Найти среднюю стоимость заказа для каждого клиента
-- Пояснение: Подзапрос в FROM создает временную таблицу, с которой работает внешний запрос
-- Это полезно для многоэтапных вычислений

SELECT 
    customer_id,
    AVG(order_total) as avg_order_total
FROM (
    SELECT 
        o.customer_id,
        SUM(oi.quantity * p.product_price) as order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.order_id, o.customer_id
) as customer_orders
GROUP BY customer_id;

-- Ожидаемый результат:
-- customer_id | avg_order_total
-- 1           | 26000.00  (50000 + 2000) / 2
-- 2           | 50000.00

-- ПРИМЕР 2.6: Коррелированный подзапрос
-- Задача: Для каждого клиента найти дату последнего заказа
-- Пояснение: Подзапрос выполняется для каждой строки customers
-- Использует значение c.customer_id из внешнего запроса

SELECT 
    c.customer_name,
    (SELECT MAX(order_date) 
     FROM orders o 
     WHERE o.customer_id = c.customer_id) as last_order_date
FROM customers c;

-- Ожидаемый результат:
-- customer_name | last_order_date
-- Иван Иванов  | 2024-01-20
-- Петр Петров  | 2024-01-25

-- ПРИМЕР 2.7: Подзапрос в SELECT с агрегацией
-- Задача: Показать цену каждого продукта, среднюю цену и разницу
-- Пояснение: Подзапрос вычисляет среднюю цену один раз и используется для сравнения

SELECT 
    product_name,
    product_price,
    (SELECT AVG(product_price) FROM products) as avg_price,
    product_price - (SELECT AVG(product_price) FROM products) as price_diff
FROM products;

-- Ожидаемый результат (если avg_price = 25500):
-- product_name | product_price | avg_price | price_diff
-- Ноутбук      | 50000.00      | 25500.00  | 24500.00
-- Мышь         | 1000.00       | 25500.00  | -24500.00

-- ============================================
-- 3. ОКОННЫЕ ФУНКЦИИ (WINDOW FUNCTIONS)
-- ============================================

-- ТЕОРИЯ:
-- Оконные функции выполняют вычисления над набором строк, связанных с текущей строкой
-- КЛЮЧЕВОЕ ОТЛИЧИЕ от GROUP BY: результат не группируется, все строки остаются

-- Синтаксис:
-- function_name() OVER (
--     [PARTITION BY column1, column2, ...]  -- разбиение на группы
--     [ORDER BY column1, column2, ...]       -- сортировка внутри окна
--     [ROWS/RANGE BETWEEN ... AND ...]      -- границы окна
-- )

-- Типы оконных функций:
-- 1. Ранжирующие: ROW_NUMBER(), RANK(), DENSE_RANK(), NTILE()
-- 2. Агрегатные: SUM(), AVG(), COUNT(), MAX(), MIN()
-- 3. Смещения: LAG(), LEAD(), FIRST_VALUE(), LAST_VALUE()
-- 4. Аналитические: PERCENT_RANK(), CUME_DIST()

-- ПРИМЕР 3.1: ROW_NUMBER() - нумерация строк
-- Задача: Пронумеровать заказы каждого клиента по дате (от новых к старым)
-- Пояснение: ROW_NUMBER() присваивает уникальный номер каждой строке в окне
-- PARTITION BY customer_id - отдельная нумерация для каждого клиента
-- ORDER BY order_date DESC - сортировка по дате (новые первые)

SELECT 
    customer_id,
    order_date,
    order_total,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) as order_rank
FROM (
    SELECT 
        o.customer_id,
        o.order_date,
        SUM(oi.quantity * p.product_price) as order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.order_id, o.customer_id, o.order_date
) as order_totals;

-- Ожидаемый результат:
-- customer_id | order_date | order_total | order_rank
-- 1           | 2024-01-20| 2000.00     | 1
-- 1           | 2024-01-15| 50000.00    | 2
-- 2           | 2024-01-25| 50000.00    | 1

-- ПРИМЕР 3.2: RANK() и DENSE_RANK() - ранжирование
-- Задача: Ранжировать продукты по цене
-- Пояснение: 
-- RANK() - пропускает номера при равенстве (1, 2, 2, 4)
-- DENSE_RANK() - не пропускает номера (1, 2, 2, 3)

SELECT 
    product_name,
    product_price,
    RANK() OVER (ORDER BY product_price DESC) as price_rank,
    DENSE_RANK() OVER (ORDER BY product_price DESC) as price_dense_rank
FROM products;

-- Ожидаемый результат:
-- product_name | product_price | price_rank | price_dense_rank
-- Ноутбук      | 50000.00      | 1          | 1
-- Мышь         | 1000.00       | 2          | 2

-- Если добавить еще один продукт за 50000:
-- product_name | product_price | price_rank | price_dense_rank
-- Ноутбук      | 50000.00      | 1          | 1
-- Планшет      | 50000.00      | 1          | 1
-- Мышь         | 1000.00       | 3          | 2  <- RANK пропустил 2, DENSE_RANK нет

-- ПРИМЕР 3.3: Агрегатные оконные функции
-- Задача: Для каждого заказа показать накопительную сумму и средний чек клиента
-- Пояснение:
-- SUM() OVER (PARTITION BY ... ORDER BY ...) - накопительная сумма (running total)
-- AVG() OVER (PARTITION BY ...) - среднее по группе
-- COUNT() OVER (PARTITION BY ...) - количество в группе

SELECT 
    customer_id,
    order_date,
    order_total,
    SUM(order_total) OVER (PARTITION BY customer_id ORDER BY order_date) as running_total,
    AVG(order_total) OVER (PARTITION BY customer_id) as avg_customer_order,
    COUNT(*) OVER (PARTITION BY customer_id) as total_orders
FROM (
    SELECT 
        o.customer_id,
        o.order_date,
        SUM(oi.quantity * p.product_price) as order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.order_id, o.customer_id, o.order_date
) as order_totals;

-- Ожидаемый результат:
-- customer_id | order_date | order_total | running_total | avg_customer_order | total_orders
-- 1           | 2024-01-15| 50000.00    | 50000.00      | 26000.00          | 2
-- 1           | 2024-01-20| 2000.00     | 52000.00      | 26000.00          | 2
-- 2           | 2024-01-25| 50000.00    | 50000.00      | 50000.00          | 1

-- ПРИМЕР 3.4: LAG() и LEAD() - доступ к предыдущей/следующей строке
-- Задача: Сравнить дневную выручку с предыдущим и следующим днем
-- Пояснение:
-- LAG(column, n) - значение из n-й строки назад (по умолчанию n=1)
-- LEAD(column, n) - значение из n-й строки вперед (по умолчанию n=1)
-- Для первой строки LAG возвращает NULL, для последней LEAD возвращает NULL

SELECT 
    order_date,
    order_total,
    LAG(order_total, 1) OVER (ORDER BY order_date) as previous_order,
    LEAD(order_total, 1) OVER (ORDER BY order_date) as next_order,
    order_total - LAG(order_total, 1) OVER (ORDER BY order_date) as change_from_previous
FROM (
    SELECT 
        o.order_date,
        SUM(oi.quantity * p.product_price) as order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.order_date
) as daily_totals;

-- Ожидаемый результат:
-- order_date | order_total | previous_order | next_order | change_from_previous
-- 2024-01-15 | 50000.00    | NULL          | 2000.00    | NULL
-- 2024-01-20 | 2000.00     | 50000.00      | 50000.00   | -48000.00
-- 2024-01-25 | 50000.00    | 2000.00       | NULL       | 48000.00

-- ПРИМЕР 3.5: FIRST_VALUE() и LAST_VALUE()
-- Задача: Показать первый и последний заказ каждого клиента
-- Пояснение:
-- FIRST_VALUE() - первое значение в окне
-- LAST_VALUE() - последнее значение в окне
-- ВАЖНО: Для LAST_VALUE нужно указать ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
-- Иначе LAST_VALUE вернет значение текущей строки, а не последней в окне

SELECT 
    customer_id,
    order_date,
    order_total,
    FIRST_VALUE(order_total) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as first_order_total,
    LAST_VALUE(order_total) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_order_total
FROM (
    SELECT 
        o.customer_id,
        o.order_date,
        SUM(oi.quantity * p.product_price) as order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.order_id, o.customer_id, o.order_date
) as order_totals;

-- Ожидаемый результат:
-- customer_id | order_date | order_total | first_order_total | last_order_total
-- 1           | 2024-01-15| 50000.00    | 50000.00         | 2000.00
-- 1           | 2024-01-20| 2000.00     | 50000.00         | 2000.00
-- 2           | 2024-01-25| 50000.00    | 50000.00         | 50000.00

-- ПРИМЕР 3.6: NTILE() - разбиение на группы
-- Задача: Разделить клиентов на 4 группы (квартили) по сумме покупок
-- Пояснение: NTILE(n) делит строки на n примерно равных групп
-- Если строк 10 и n=4: группы будут 3, 3, 2, 2 (не 2.5, поэтому неравномерно)

SELECT 
    customer_id,
    total_spent,
    NTILE(4) OVER (ORDER BY total_spent DESC) as quartile
FROM (
    SELECT 
        c.customer_id,
        COALESCE(SUM(oi.quantity * p.product_price), 0) as total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN products p ON oi.product_id = p.product_id
    GROUP BY c.customer_id
) as customer_totals;

-- Ожидаемый результат (если 4 клиента):
-- customer_id | total_spent | quartile
-- 2           | 50000.00   | 1  (топ 25%)
-- 1           | 52000.00   | 1  (топ 25%)
-- 3           | 10000.00    | 3  (нижние 25-50%)
-- 4           | 0.00        | 4  (нижние 0-25%)

-- ПРИМЕР 3.7: Оконные рамки (FRAME)
-- Задача: Вычислить скользящее среднее за 3 дня и среднее за 7 дней
-- Пояснение:
-- ROWS BETWEEN - работает с физическими строками (2 строки назад, текущая = 3 строки)
-- RANGE BETWEEN - работает с логическими значениями (7 дней назад по дате)
-- UNBOUNDED PRECEDING - от начала окна
-- UNBOUNDED FOLLOWING - до конца окна
-- CURRENT ROW - текущая строка
-- n PRECEDING - n строк/значений назад
-- n FOLLOWING - n строк/значений вперед

SELECT 
    order_date,
    order_total,
    SUM(order_total) OVER (
        ORDER BY order_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as three_day_sum,
    AVG(order_total) OVER (
        ORDER BY order_date 
        RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
    ) as seven_day_avg
FROM (
    SELECT 
        o.order_date,
        SUM(oi.quantity * p.product_price) as order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.order_date
) as daily_totals;

-- Ожидаемый результат:
-- order_date | order_total | three_day_sum | seven_day_avg
-- 2024-01-15 | 50000.00    | 50000.00      | 50000.00
-- 2024-01-20 | 2000.00     | 52000.00      | 26000.00
-- 2024-01-25 | 50000.00    | 102000.00     | 34666.67

-- ============================================
-- 4. ИНДЕКСЫ
-- ============================================

-- ТЕОРИЯ:
-- Индекс - структура данных, которая ускоряет поиск данных в таблице
-- Аналогия: как оглавление в книге - не нужно листать все страницы

-- Типы индексов:
-- 1. B-tree (B-дерево) - самый распространенный, для большинства случаев
-- 2. Hash - для точного совпадения (=), быстрее B-tree, но ограниченнее
-- 3. GIN (Generalized Inverted Index) - для массивов, полнотекстового поиска
-- 4. GiST (Generalized Search Tree) - для геоданных, полнотекстового поиска
-- 5. BRIN (Block Range Index) - для больших таблиц с упорядоченными данными

-- Когда использовать индексы:
-- + Частые запросы с WHERE, JOIN, ORDER BY
-- + Колонки с высокой селективностью (много уникальных значений)
-- + Внешние ключи (для JOIN)

-- Когда НЕ использовать:
-- - Маленькие таблицы (< 1000 строк)
-- - Частые INSERT/UPDATE/DELETE (замедляют операции)
-- - Колонки с низкой селективностью (мало уникальных значений, например: пол, статус)

-- ПРИМЕР 4.1: Простой индекс (B-tree)
-- Задача: Ускорить поиск клиентов по email
-- Пояснение: Создает B-tree индекс на колонке customer_email
-- После создания запросы WHERE customer_email = '...' будут работать быстрее

CREATE INDEX idx_customer_email ON customers(customer_email);

-- Использование:
-- SELECT * FROM customers WHERE customer_email = 'ivan@mail.ru';
-- Без индекса: Seq Scan (сканирование всех строк) - медленно
-- С индексом: Index Scan - быстро

-- ПРИМЕР 4.2: Составной индекс (много колонок)
-- Задача: Ускорить поиск заказов по клиенту и дате
-- Пояснение: Индекс создается на нескольких колонках
-- ВАЖНО: Порядок колонок критичен! Индекс используется слева направо

CREATE INDEX idx_order_customer_date ON orders(customer_id, order_date);

-- Использование индекса:
-- WHERE customer_id = 1 - использует индекс (первая колонка)
-- WHERE customer_id = 1 AND order_date >= '2024-01-01' - использует индекс (обе колонки)
-- WHERE order_date >= '2024-01-01' - НЕ использует индекс (нет customer_id)
-- WHERE order_date >= '2024-01-01' AND customer_id = 1 - использует индекс (оптимизатор переставит)

-- ПРИМЕР 4.3: Уникальный индекс
-- Задача: Гарантировать уникальность email
-- Пояснение: Уникальный индекс не позволяет дублировать значения
-- Автоматически создается при PRIMARY KEY и UNIQUE constraint

CREATE UNIQUE INDEX idx_unique_email ON customers(customer_email);

-- Попытка вставить дубликат вызовет ошибку:
-- INSERT INTO customers VALUES (3, 'Test', 'ivan@mail.ru');
-- ERROR: duplicate key value violates unique constraint

-- ПРИМЕР 4.4: Частичный индекс (только для части данных)
-- Задача: Создать индекс только для недавних заказов
-- Пояснение: Индекс создается только для строк, удовлетворяющих условию
-- Преимущества: меньше размер, быстрее обновление, быстрее запросы по условию

CREATE INDEX idx_recent_orders ON orders(order_date) 
WHERE order_date >= '2024-01-01';

-- Использование:
-- WHERE order_date >= '2024-01-01' - использует индекс
-- WHERE order_date < '2024-01-01' - НЕ использует индекс (не покрыто условием)

-- ПРИМЕР 4.5: Индекс для полнотекстового поиска (PostgreSQL)
-- Задача: Ускорить поиск по названию продукта
-- Пояснение: GIN индекс для полнотекстового поиска
-- to_tsvector() преобразует текст в вектор для поиска

CREATE INDEX idx_product_search ON products USING GIN(to_tsvector('russian', product_name));

-- Использование:
-- SELECT * FROM products 
-- WHERE to_tsvector('russian', product_name) @@ to_tsquery('russian', 'ноутбук');

-- ПРИМЕР 4.6: Удаление индекса
-- Пояснение: Индексы можно удалять, если они больше не нужны
-- IF EXISTS предотвращает ошибку, если индекс не существует

DROP INDEX IF EXISTS idx_customer_email;

-- ПРИМЕР 4.7: Проверка использования индексов
-- Используйте EXPLAIN ANALYZE для проверки (см. раздел 7)

-- Обновление статистики (важно после создания индексов):
ANALYZE customers;
ANALYZE orders;

-- ============================================
-- 5. ТРИГГЕРЫ
-- ============================================

-- ТЕОРИЯ:
-- Триггер - автоматически выполняемая функция при определенных событиях
-- События: INSERT, UPDATE, DELETE
-- Время выполнения: BEFORE (до операции) или AFTER (после операции)
-- Уровень: FOR EACH ROW (для каждой строки) или FOR EACH STATEMENT (для оператора)

-- Типы триггеров:
-- 1. BEFORE INSERT/UPDATE/DELETE - валидация, модификация данных перед операцией
-- 2. AFTER INSERT/UPDATE/DELETE - логирование, обновление связанных таблиц

-- Специальные переменные (PostgreSQL):
-- NEW - новая строка (для INSERT, UPDATE)
-- OLD - старая строка (для UPDATE, DELETE)
-- TG_OP - тип операции ('INSERT', 'UPDATE', 'DELETE')
-- TG_TABLE_NAME - имя таблицы

-- ПРИМЕР 5.1: Триггер для логирования изменений
-- Задача: Сохранять историю всех изменений в таблице orders
-- Пояснение: После каждой операции INSERT/UPDATE/DELETE запись сохраняется в order_history

CREATE TABLE order_history (
    history_id SERIAL PRIMARY KEY,
    order_id INT,
    action VARCHAR(10),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB
);

CREATE OR REPLACE FUNCTION log_order_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO order_history (order_id, action, new_data)
        VALUES (NEW.order_id, 'INSERT', row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO order_history (order_id, action, old_data, new_data)
        VALUES (NEW.order_id, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO order_history (order_id, action, old_data)
        VALUES (OLD.order_id, 'DELETE', row_to_json(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_orders
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW
EXECUTE FUNCTION log_order_changes();

-- Тестирование:
-- INSERT INTO orders VALUES (4, 1, '2024-02-01');
-- Результат в order_history:
-- history_id | order_id | action | changed_at           | old_data | new_data
-- 1          | 4        | INSERT | 2024-02-01 10:00:00 | NULL     | {"order_id":4,"customer_id":1,"order_date":"2024-02-01"}

-- UPDATE orders SET order_date = '2024-02-02' WHERE order_id = 4;
-- Результат в order_history:
-- history_id | order_id | action | changed_at           | old_data | new_data
-- 2          | 4        | UPDATE | 2024-02-01 10:05:00 | {...}    | {...}

-- ПРИМЕР 5.2: Триггер для автоматического обновления статистики
-- Задача: Поддерживать актуальную статистику клиентов
-- Пояснение: При добавлении/удалении заказа автоматически обновляется статистика

CREATE TABLE customer_stats (
    customer_id INT PRIMARY KEY,
    total_orders INT DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    last_order_date DATE
);

CREATE OR REPLACE FUNCTION update_customer_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE customer_stats
        SET 
            total_orders = total_orders + 1,
            total_spent = total_spent + (
                SELECT SUM(oi.quantity * p.product_price)
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = NEW.order_id
            ),
            last_order_date = NEW.order_date
        WHERE customer_id = NEW.customer_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE customer_stats
        SET 
            total_orders = GREATEST(total_orders - 1, 0),
            total_spent = GREATEST(total_spent - (
                SELECT SUM(oi.quantity * p.product_price)
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = OLD.order_id
            ), 0)
        WHERE customer_id = OLD.customer_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_stats
AFTER INSERT OR DELETE ON orders
FOR EACH ROW
EXECUTE FUNCTION update_customer_stats();

-- ПРИМЕР 5.3: Триггер BEFORE для валидации
-- Задача: Проверить, что дата заказа не в будущем
-- Пояснение: BEFORE триггер может предотвратить операцию, выбросив исключение

CREATE OR REPLACE FUNCTION validate_order_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.order_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Order date cannot be in the future';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_order
BEFORE INSERT OR UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION validate_order_date();

-- Тестирование:
-- INSERT INTO orders VALUES (5, 1, '2025-01-01');
-- ERROR: Order date cannot be in the future

-- ПРИМЕР 5.4: Удаление триггера
-- Пояснение: Сначала удаляется триггер, потом функция

DROP TRIGGER IF EXISTS trigger_log_orders ON orders;
DROP FUNCTION IF EXISTS log_order_changes();

-- ============================================
-- 6. ОПТИМИЗАЦИЯ ЗАПРОСОВ
-- ============================================

-- ТЕОРИЯ:
-- Оптимизация запросов - улучшение производительности SQL запросов
-- Основные принципы:
-- 1. Использовать индексы
-- 2. Избегать полного сканирования таблиц (Seq Scan)
-- 3. Минимизировать количество обрабатываемых строк
-- 4. Использовать эффективные JOIN'ы
-- 5. Избегать функций в WHERE (мешают использованию индексов)

-- ПРИМЕР 6.1: JOIN вместо подзапросов
-- МЕДЛЕННО: Подзапрос выполняется для каждой строки или создает временную таблицу
SELECT customer_name
FROM customers
WHERE customer_id IN (SELECT customer_id FROM orders WHERE order_date >= '2024-01-01');

-- БЫСТРО: JOIN обычно оптимизируется лучше
SELECT DISTINCT c.customer_name
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01';

-- ПРИМЕР 6.2: EXISTS вместо IN для больших наборов
-- МЕДЛЕННО: IN создает список всех значений и проверяет вхождение
SELECT * FROM customers WHERE customer_id IN (SELECT customer_id FROM orders);

-- БЫСТРО: EXISTS останавливается при первом совпадении
SELECT * FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);

-- ПРИМЕР 6.3: Ограничение выборки (LIMIT)
-- Всегда используйте LIMIT, если нужны не все строки
SELECT * FROM orders ORDER BY order_date DESC LIMIT 10;

-- ПРИМЕР 6.4: Выбор только нужных колонок
-- ПЛОХО: SELECT * загружает все колонки
SELECT * FROM customers;

-- ХОРОШО: Выбирайте только нужные колонки
SELECT customer_id, customer_name FROM customers;

-- ПРИМЕР 6.5: Использование индексов в WHERE
-- ХОРОШО: Использует индекс на customer_id и order_date
SELECT * FROM orders WHERE customer_id = 123 AND order_date >= '2024-01-01';

-- ПЛОХО: Если нет индекса на order_total, будет Seq Scan
SELECT * FROM orders WHERE order_total > 1000;

-- ПРИМЕР 6.6: Избегание функций в WHERE
-- ПЛОХО: Функция DATE_TRUNC не позволяет использовать индекс на order_date
SELECT * FROM orders WHERE DATE_TRUNC('month', order_date) = '2024-01-01';

-- ХОРОШО: Прямое сравнение позволяет использовать индекс
SELECT * FROM orders 
WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01';

-- ПРИМЕР 6.7: Оптимизация GROUP BY
-- ВАЖНО: Все неагрегированные колонки должны быть в GROUP BY
SELECT customer_id, order_date, SUM(order_total)
FROM orders
GROUP BY customer_id, order_date;

-- ПРИМЕР 6.8: UNION ALL вместо UNION
-- UNION удаляет дубликаты (медленно), UNION ALL не удаляет (быстро)
-- Используйте UNION ALL, если дубликаты невозможны или не важны
SELECT customer_id FROM orders WHERE order_date >= '2024-01-01'
UNION ALL
SELECT customer_id FROM orders WHERE order_date < '2024-01-01';

-- ============================================
-- 7. EXPLAIN ANALYZE
-- ============================================

-- ТЕОРИЯ:
-- EXPLAIN - показывает план выполнения запроса БЕЗ выполнения
-- EXPLAIN ANALYZE - выполняет запрос и показывает реальную статистику
-- Используется для оптимизации запросов и проверки использования индексов

-- Ключевые элементы плана:
-- 1. Seq Scan (Sequential Scan) - последовательное сканирование всех строк - МЕДЛЕННО
-- 2. Index Scan - сканирование через индекс - БЫСТРО
-- 3. Index Only Scan - сканирование только индекса (данные из таблицы не нужны) - ОЧЕНЬ БЫСТРО
-- 4. Hash Join - соединение через хеш-таблицу - для больших таблиц
-- 5. Merge Join - соединение через сортировку - для отсортированных данных
-- 6. Nested Loop - вложенный цикл - для маленьких таблиц

-- Метрики:
-- - Planning Time - время планирования запроса
-- - Execution Time - реальное время выполнения
-- - Rows - количество обработанных строк
-- - Cost - оценка стоимости операции (меньше = лучше)
-- - Buffers - количество прочитанных блоков

-- ПРИМЕР 7.1: Базовый EXPLAIN
-- Показывает план БЕЗ выполнения запроса
EXPLAIN SELECT * FROM orders WHERE customer_id = 123;

-- Пример вывода:
-- Seq Scan on orders  (cost=0.00..25.00 rows=1 width=20)
--   Filter: (customer_id = 123)
-- Seq Scan означает, что индекс не используется!

-- ПРИМЕР 7.2: EXPLAIN ANALYZE
-- Выполняет запрос и показывает реальную статистику
EXPLAIN ANALYZE 
SELECT c.customer_name, SUM(oi.quantity * p.product_price) as total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= '2024-01-01'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC
LIMIT 10;

-- Пример вывода:
-- Limit  (cost=... rows=10 width=40) (actual time=0.123..0.456 rows=10 loops=1)
--   ->  Sort  (cost=... rows=100 width=40) (actual time=0.120..0.450 rows=10 loops=1)
--         Sort Key: (sum(...)) DESC
--         ->  Hash Join  (cost=... rows=100 width=40) (actual time=0.050..0.300 rows=100 loops=1)
--               Hash Cond: (o.customer_id = c.customer_id)
--               ->  Seq Scan on orders o  (cost=0.00..25.00 rows=100 width=8) (actual time=0.010..0.050 rows=100 loops=1)
--                     Filter: (order_date >= '2024-01-01'::date)
--               ->  Hash  (cost=15.00..15.00 rows=1000 width=36) (actual time=0.020..0.020 rows=1000 loops=1)
--                     ->  Seq Scan on customers c  (cost=0.00..15.00 rows=1000 width=36) (actual time=0.005..0.015 rows=1000 loops=1)
-- Planning Time: 0.100 ms
-- Execution Time: 0.500 ms

-- ПРИМЕР 7.3: EXPLAIN с форматом JSON
-- Удобно для программного анализа
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM orders WHERE customer_id = 123;

-- ПРИМЕР 7.4: Проверка использования индекса
-- Если видите "Seq Scan" - индекс не используется
-- Решения:
-- 1. Создать индекс: CREATE INDEX idx_customer_id ON orders(customer_id);
-- 2. Обновить статистику: ANALYZE orders;
-- 3. Пересмотреть условие WHERE (избегать функций)

-- После создания индекса:
-- Index Scan using idx_customer_id on orders  (cost=0.29..8.31 rows=1 width=20) (actual time=0.015..0.016 rows=1 loops=1)
--   Index Cond: (customer_id = 123)
-- Теперь используется Index Scan - хорошо!

-- ============================================
-- ПРАКТИЧЕСКИЕ ПРИМЕРЫ КОМБИНАЦИЙ
-- ============================================

-- ПРИМЕР КОМБИНАЦИИ 1: Топ-5 клиентов с использованием оконных функций
-- Задача: Найти топ-5 клиентов по сумме покупок с их рангом
-- Использует: JOIN, GROUP BY, оконные функции, подзапросы

SELECT 
    customer_name,
    total_spent,
    rank_position
FROM (
    SELECT 
        c.customer_name,
        SUM(oi.quantity * p.product_price) as total_spent,
        RANK() OVER (ORDER BY SUM(oi.quantity * p.product_price) DESC) as rank_position
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY c.customer_id, c.customer_name
) as ranked_customers
WHERE rank_position <= 5;

-- Ожидаемый результат:
-- customer_name | total_spent | rank_position
-- Иван Иванов  | 52000.00    | 1
-- Петр Петров  | 50000.00    | 2

-- ПРИМЕР КОМБИНАЦИИ 2: Сравнение с предыдущим периодом
-- Задача: Сравнить выручку по месяцам с предыдущим месяцем
-- Использует: DATE_TRUNC, LAG, оконные функции, подзапросы

SELECT 
    DATE_TRUNC('month', order_date) as month,
    SUM(order_total) as month_total,
    LAG(SUM(order_total)) OVER (ORDER BY DATE_TRUNC('month', order_date)) as previous_month,
    SUM(order_total) - LAG(SUM(order_total)) OVER (ORDER BY DATE_TRUNC('month', order_date)) as change
FROM (
    SELECT 
        o.order_date,
        SUM(oi.quantity * p.product_price) as order_total
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.order_id, o.order_date
) as order_totals
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Ожидаемый результат:
-- month       | month_total | previous_month | change
-- 2024-01-01  | 102000.00   | NULL           | NULL
-- 2024-02-01  | 50000.00    | 102000.00      | -52000.00

-- ПРИМЕР КОМБИНАЦИИ 3: Процент от общего (оконные функции)
-- Задача: Показать долю каждого продукта в общей выручке
-- Использует: JOIN, GROUP BY, оконные функции с OVER()

SELECT 
    product_name,
    product_price,
    SUM(oi.quantity) as total_sold,
    SUM(oi.quantity * p.product_price) as revenue,
    ROUND(
        100.0 * SUM(oi.quantity * p.product_price) / 
        SUM(SUM(oi.quantity * p.product_price)) OVER (), 
        2
    ) as revenue_percent
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, product_name, product_price
ORDER BY revenue DESC;

-- Ожидаемый результат:
-- product_name | product_price | total_sold | revenue  | revenue_percent
-- Ноутбук      | 50000.00      | 2         | 100000.00| 96.15
-- Мышь         | 1000.00       | 2         | 2000.00  | 1.92
