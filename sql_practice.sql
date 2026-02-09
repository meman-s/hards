-- ============================================
-- SQL ПРАКТИКА: Примеры и объяснения
-- ============================================

-- ============================================
-- 1. НОРМАЛИЗАЦИЯ БАЗЫ ДАННЫХ
-- ============================================

-- Нормализация - процесс организации данных для уменьшения избыточности
-- Основные нормальные формы:
-- 1NF: Каждая ячейка содержит атомарное значение
-- 2NF: 1NF + нет частичных зависимостей от составного ключа
-- 3NF: 2NF + нет транзитивных зависимостей

-- Пример ДО нормализации (плохая структура):
CREATE TABLE bad_orders (
    order_id INT,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    product_name VARCHAR(100),
    product_price DECIMAL(10,2),
    quantity INT,
    order_date DATE
);

-- Пример ПОСЛЕ нормализации (хорошая структура):
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

-- ============================================
-- 2. ПОДЗАПРОСЫ (SUBQUERIES)
-- ============================================

-- Подзапрос - запрос внутри другого запроса
-- Типы: коррелированные и некоррелированные

-- 2.1. Скалярный подзапрос (возвращает одно значение)
SELECT 
    customer_name,
    (SELECT COUNT(*) FROM orders WHERE orders.customer_id = customers.customer_id) as order_count
FROM customers;

-- 2.2. Подзапрос в WHERE (IN, EXISTS, NOT EXISTS)
-- IN - проверка вхождения в список
SELECT customer_name
FROM customers
WHERE customer_id IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE order_date >= '2024-01-01'
);

-- EXISTS - проверка существования (часто быстрее чем IN)
SELECT customer_name
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id 
    AND o.order_date >= '2024-01-01'
);

-- NOT EXISTS - проверка отсутствия
SELECT customer_name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
);

-- 2.3. Подзапрос в FROM (производная таблица)
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

-- 2.4. Коррелированный подзапрос (зависит от внешнего запроса)
SELECT 
    c.customer_name,
    (SELECT MAX(order_date) 
     FROM orders o 
     WHERE o.customer_id = c.customer_id) as last_order_date
FROM customers c;

-- 2.5. Подзапрос в SELECT с агрегацией
SELECT 
    product_name,
    product_price,
    (SELECT AVG(product_price) FROM products) as avg_price,
    product_price - (SELECT AVG(product_price) FROM products) as price_diff
FROM products;

-- ============================================
-- 3. ОКОННЫЕ ФУНКЦИИ (WINDOW FUNCTIONS)
-- ============================================

-- Оконные функции выполняют вычисления над набором строк,
-- связанных с текущей строкой, БЕЗ группировки результата

-- 3.1. ROW_NUMBER() - нумерация строк
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

-- 3.2. RANK() и DENSE_RANK() - ранжирование
SELECT 
    product_name,
    product_price,
    RANK() OVER (ORDER BY product_price DESC) as price_rank,
    DENSE_RANK() OVER (ORDER BY product_price DESC) as price_dense_rank
FROM products;

-- RANK: 1, 2, 2, 4 (пропускает номера при равенстве)
-- DENSE_RANK: 1, 2, 2, 3 (не пропускает номера)

-- 3.3. SUM(), AVG(), COUNT() - агрегатные оконные функции
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

-- 3.4. LAG() и LEAD() - доступ к предыдущей/следующей строке
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

-- 3.5. FIRST_VALUE() и LAST_VALUE() - первое/последнее значение в окне
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

-- 3.6. NTILE() - разбиение на группы
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

-- 3.7. Оконные рамки (FRAME)
-- ROWS BETWEEN - физические строки
-- RANGE BETWEEN - логические значения
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
    JOIN products p ON oi.product_id = p.product_price
    GROUP BY o.order_date
) as daily_totals;

-- ============================================
-- 4. ИНДЕКСЫ
-- ============================================

-- Индексы ускоряют поиск данных, но замедляют INSERT/UPDATE/DELETE
-- Используются автоматически при WHERE, JOIN, ORDER BY

-- 4.1. Простой индекс (B-tree)
CREATE INDEX idx_customer_email ON customers(customer_email);

-- 4.2. Составной индекс (много колонок)
CREATE INDEX idx_order_customer_date ON orders(customer_id, order_date);

-- Порядок колонок важен! Используется слева направо
-- WHERE customer_id = 1 - использует индекс
-- WHERE order_date = '2024-01-01' - НЕ использует индекс (если нет customer_id)

-- 4.3. Уникальный индекс
CREATE UNIQUE INDEX idx_unique_email ON customers(customer_email);

-- 4.4. Частичный индекс (только для части данных)
CREATE INDEX idx_recent_orders ON orders(order_date) 
WHERE order_date >= '2024-01-01';

-- 4.5. Индекс для полнотекстового поиска (PostgreSQL)
CREATE INDEX idx_product_search ON products USING GIN(to_tsvector('russian', product_name));

-- 4.6. Удаление индекса
DROP INDEX IF EXISTS idx_customer_email;

-- 4.7. Проверка использования индексов
-- В PostgreSQL используйте EXPLAIN ANALYZE (см. раздел 7)

-- ============================================
-- 5. ТРИГГЕРЫ
-- ============================================

-- Триггеры - автоматически выполняемый код при событиях (INSERT/UPDATE/DELETE)

-- 5.1. Триггер для логирования изменений (PostgreSQL)
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

-- 5.2. Триггер для автоматического обновления статистики
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

-- 5.3. Триггер BEFORE для валидации
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

-- 5.4. Удаление триггера
DROP TRIGGER IF EXISTS trigger_log_orders ON orders;
DROP FUNCTION IF EXISTS log_order_changes();

-- ============================================
-- 6. ОПТИМИЗАЦИЯ ЗАПРОСОВ
-- ============================================

-- 6.1. Использование JOIN вместо подзапросов (часто быстрее)
-- МЕДЛЕННО:
SELECT customer_name
FROM customers
WHERE customer_id IN (SELECT customer_id FROM orders WHERE order_date >= '2024-01-01');

-- БЫСТРО:
SELECT DISTINCT c.customer_name
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01';

-- 6.2. Использование EXISTS вместо IN для больших наборов
-- МЕДЛЕННО (если подзапрос возвращает много строк):
SELECT * FROM customers WHERE customer_id IN (SELECT customer_id FROM orders);

-- БЫСТРО:
SELECT * FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);

-- 6.3. Ограничение выборки (LIMIT)
SELECT * FROM orders ORDER BY order_date DESC LIMIT 10;

-- 6.4. Выбор только нужных колонок (не SELECT *)
SELECT customer_id, customer_name FROM customers;

-- 6.5. Использование индексов в WHERE
-- ХОРОШО (использует индекс):
SELECT * FROM orders WHERE customer_id = 123 AND order_date >= '2024-01-01';

-- ПЛОХО (не использует индекс, если нет индекса на order_total):
SELECT * FROM orders WHERE order_total > 1000;

-- 6.6. Избегание функций в WHERE (не позволяет использовать индекс)
-- ПЛОХО:
SELECT * FROM orders WHERE DATE_TRUNC('month', order_date) = '2024-01-01';

-- ХОРОШО:
SELECT * FROM orders 
WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01';

-- 6.7. Оптимизация GROUP BY
-- Добавьте все неагрегированные колонки в GROUP BY
SELECT customer_id, order_date, SUM(order_total)
FROM orders
GROUP BY customer_id, order_date;

-- 6.8. Использование UNION ALL вместо UNION (если дубликаты не важны)
-- UNION ALL быстрее, т.к. не удаляет дубликаты
SELECT customer_id FROM orders WHERE order_date >= '2024-01-01'
UNION ALL
SELECT customer_id FROM orders WHERE order_date < '2024-01-01';

-- ============================================
-- 7. EXPLAIN ANALYZE
-- ============================================

-- EXPLAIN ANALYZE показывает план выполнения запроса и реальное время

-- 7.1. Базовый EXPLAIN
EXPLAIN SELECT * FROM orders WHERE customer_id = 123;

-- 7.2. EXPLAIN ANALYZE (выполняет запрос и показывает статистику)
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

-- Что смотреть в выводе:
-- - Seq Scan (последовательное сканирование) - медленно, нужен индекс
-- - Index Scan / Index Only Scan - хорошо, использует индекс
-- - Hash Join / Merge Join - типы соединений
-- - Execution Time - реальное время выполнения
-- - Planning Time - время планирования запроса
-- - Rows - количество обработанных строк
-- - Cost - оценка стоимости операции

-- 7.3. EXPLAIN с форматом JSON (для анализа)
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM orders WHERE customer_id = 123;

-- 7.4. Проверка использования индекса
-- Если видите "Seq Scan" - индекс не используется, возможно нужно:
-- 1. Создать индекс
-- 2. Обновить статистику: ANALYZE table_name;
-- 3. Пересмотреть условие WHERE

-- ============================================
-- ПРАКТИЧЕСКИЕ ПРИМЕРЫ КОМБИНАЦИЙ
-- ============================================

-- Пример 1: Топ-5 клиентов с использованием оконных функций
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

-- Пример 2: Сравнение с предыдущим периодом
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

-- Пример 3: Процент от общего (оконные функции)
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
