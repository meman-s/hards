-- ============================================
-- ОКОННЫЕ ФУНКЦИИ В SQL
-- Полное руководство: теория и практика
-- ============================================

-- ============================================
-- ЧАСТЬ 1: ТЕОРИЯ
-- ============================================

-- Оконные функции (Window Functions) позволяют выполнять вычисления
-- над набором строк, связанных с текущей строкой, БЕЗ группировки результата.
-- В отличие от GROUP BY, они сохраняют все строки исходного набора.

-- СИНТАКСИС:
-- WINDOW_FUNCTION() OVER (
--     [PARTITION BY column(s)]  -- разбивает данные на группы
--     [ORDER BY column(s)]      -- сортирует строки внутри окна
--     [ROWS/RANGE BETWEEN ...]  -- определяет границы окна
-- )

-- ============================================
-- ЧАСТЬ 2: ТИПЫ ОКОННЫХ ФУНКЦИЙ
-- ============================================

-- ============================================
-- 2.1. АГРЕГАТНЫЕ ФУНКЦИИ (как оконные)
-- ============================================

-- SUM, AVG, COUNT, MIN, MAX можно использовать как оконные функции

-- Пример: Сумма и среднее по отделам (сохраняя все строки)
SELECT 
    employee_id,
    name,
    department,
    salary,
    SUM(salary) OVER (PARTITION BY department) AS dept_total_salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary,
    COUNT(*) OVER (PARTITION BY department) AS dept_employee_count,
    MAX(salary) OVER (PARTITION BY department) AS dept_max_salary,
    MIN(salary) OVER (PARTITION BY department) AS dept_min_salary
FROM employees;

-- Пример: Процент от общей суммы
SELECT 
    product_name,
    revenue,
    revenue * 100.0 / SUM(revenue) OVER () AS percent_of_total
FROM sales;

-- ============================================
-- 2.2. РАНЖИРУЮЩИЕ ФУНКЦИИ
-- ============================================

-- ROW_NUMBER() - уникальный номер строки (1, 2, 3, 4...)
-- RANK() - ранг с пропусками (1, 2, 2, 4...)
-- DENSE_RANK() - ранг без пропусков (1, 2, 2, 3...)
-- NTILE(n) - разбивает на n групп

-- Пример: Ранжирование сотрудников по зарплате
SELECT 
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
    RANK() OVER (ORDER BY salary DESC) AS rank_with_gaps,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS rank_no_gaps,
    NTILE(4) OVER (ORDER BY salary DESC) AS quartile
FROM employees;

-- Пример: Топ-3 зарплаты в каждом отделе
SELECT 
    name,
    department,
    salary
FROM (
    SELECT 
        name,
        department,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
) AS ranked
WHERE rn <= 3;

-- ============================================
-- 2.3. ФУНКЦИИ СМЕЩЕНИЯ
-- ============================================

-- LAG(column, n) - значение из предыдущей строки (на n позиций назад)
-- LEAD(column, n) - значение из следующей строки (на n позиций вперед)
-- FIRST_VALUE(column) - первое значение в окне
-- LAST_VALUE(column) - последнее значение в окне

-- Пример: Сравнение с предыдущим значением
SELECT 
    date,
    sales,
    LAG(sales, 1) OVER (ORDER BY date) AS prev_day_sales,
    LEAD(sales, 1) OVER (ORDER BY date) AS next_day_sales,
    sales - LAG(sales, 1) OVER (ORDER BY date) AS day_over_day_change,
    FIRST_VALUE(sales) OVER (ORDER BY date) AS first_day_sales,
    LAST_VALUE(sales) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_day_sales
FROM daily_sales;

-- ============================================
-- 2.4. ФУНКЦИИ РАСПРЕДЕЛЕНИЯ
-- ============================================

-- PERCENT_RANK() - относительный ранг (0.0 до 1.0)
-- CUME_DIST() - кумулятивное распределение (0.0 до 1.0)

SELECT 
    name,
    salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS percent_rank,
    CUME_DIST() OVER (ORDER BY salary) AS cumulative_distribution
FROM employees;

-- ============================================
-- ЧАСТЬ 3: ОКОННЫЕ РАМКИ (FRAME)
-- ============================================

-- Оконные рамки определяют, какие строки включаются в вычисление

-- Пример: Накопительная сумма
SELECT 
    date,
    amount,
    -- Текущая строка и все предыдущие
    SUM(amount) OVER (
        ORDER BY date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    
    -- Текущая строка и предыдущие 2
    SUM(amount) OVER (
        ORDER BY date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS last_3_days_total,
    
    -- Скользящее среднее за 7 дней
    AVG(amount) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS avg_7_days,
    
    -- Текущая строка и следующие 2
    SUM(amount) OVER (
        ORDER BY date 
        ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING
    ) AS next_3_days_total
FROM daily_transactions;

-- Варианты границ:
-- UNBOUNDED PRECEDING - от начала окна
-- n PRECEDING - n строк назад
-- CURRENT ROW - текущая строка
-- n FOLLOWING - n строк вперед
-- UNBOUNDED FOLLOWING - до конца окна

-- ============================================
-- ЧАСТЬ 4: ПРАКТИЧЕСКИЕ ПРИМЕРЫ
-- ============================================

-- ============================================
-- Пример 1: Найти дубликаты
-- ============================================
SELECT
    email,
    name,
    registration_date
FROM (
    SELECT
        email,
        name,
        registration_date,
        ROW_NUMBER() OVER (PARTITION BY email ORDER BY registration_date) AS rn
    FROM users
) AS ranked
WHERE rn > 1;

-- ============================================
-- Пример 2: Разница между строками
-- ============================================
SELECT
    month,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY month) AS prev_month_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY month) AS revenue_change,
    (revenue - LAG(revenue, 1) OVER (ORDER BY month)) * 100.0 /
        LAG(revenue, 1) OVER (ORDER BY month) AS revenue_change_percent
FROM monthly_revenue;

-- ============================================
-- Пример 3: Процент от группы
-- ============================================
SELECT 
    category,
    product_name,
    sales,
    sales * 100.0 / SUM(sales) OVER (PARTITION BY category) AS percent_of_category
FROM product_sales;

-- ============================================
-- Пример 4: Скользящее среднее
-- ============================================
SELECT
    date,
    temperature,
    AVG(temperature) OVER (
        ORDER BY date
        ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
    ) AS moving_avg_5_days
FROM weather_data;

-- ============================================
-- Пример 5: Ранжирование с разбивкой
-- ============================================
SELECT 
    student_name,
    subject,
    score,
    RANK() OVER (PARTITION BY subject ORDER BY score DESC) AS subject_rank,
    RANK() OVER (ORDER BY score DESC) AS overall_rank
FROM exam_results;

-- ============================================
-- Пример 6: Первая и последняя запись в группе
-- ============================================
SELECT 
    customer_id,
    order_date,
    order_amount,
    FIRST_VALUE(order_amount) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date
    ) AS first_order_amount,
    LAST_VALUE(order_amount) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_order_amount
FROM orders;

-- ============================================
-- Пример 7: Процентный ранг
-- ============================================
SELECT 
    employee_name,
    salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS salary_percentile,
    CASE 
        WHEN PERCENT_RANK() OVER (ORDER BY salary) >= 0.9 THEN 'Top 10%'
        WHEN PERCENT_RANK() OVER (ORDER BY salary) >= 0.75 THEN 'Top 25%'
        WHEN PERCENT_RANK() OVER (ORDER BY salary) >= 0.5 THEN 'Top 50%'
        ELSE 'Bottom 50%'
    END AS salary_category
FROM employees;

-- ============================================
-- Пример 8: Разбивка на группы (NTILE)
-- ============================================
SELECT 
    customer_name,
    total_purchases,
    NTILE(4) OVER (ORDER BY total_purchases DESC) AS customer_segment
FROM customer_stats;

-- ============================================
-- Пример 9: Сравнение с предыдущим периодом
-- ============================================
SELECT 
    year,
    quarter,
    revenue,
    LAG(revenue, 4) OVER (ORDER BY year, quarter) AS revenue_same_quarter_last_year,
    revenue - LAG(revenue, 4) OVER (ORDER BY year, quarter) AS year_over_year_change
FROM quarterly_revenue;

-- ============================================
-- Пример 10: Накопительные метрики
-- ============================================
SELECT 
    date,
    new_users,
    SUM(new_users) OVER (ORDER BY date) AS total_users,
    AVG(new_users) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS avg_users_last_7_days
FROM daily_user_stats;

-- ============================================
-- ЧАСТЬ 5: СРАВНЕНИЕ С GROUP BY
-- ============================================

-- С GROUP BY (теряем детали):
-- SELECT department, AVG(salary) AS avg_salary
-- FROM employees
-- GROUP BY department;
-- Результат: только отделы и средние зарплаты

-- С оконной функцией (сохраняем детали):
-- SELECT 
--     name,
--     department,
--     salary,
--     AVG(salary) OVER (PARTITION BY department) AS avg_salary
-- FROM employees;
-- Результат: все сотрудники + средняя зарплата по отделу

-- ============================================
-- ЧАСТЬ 6: КОМБИНИРОВАНИЕ ОКОННЫХ ФУНКЦИЙ
-- ============================================

-- Можно использовать несколько оконных функций в одном запросе
SELECT 
    product_name,
    category,
    sales,
    RANK() OVER (PARTITION BY category ORDER BY sales DESC) AS category_rank,
    RANK() OVER (ORDER BY sales DESC) AS overall_rank,
    SUM(sales) OVER (PARTITION BY category) AS category_total,
    sales * 100.0 / SUM(sales) OVER () AS percent_of_total
FROM product_sales;

-- ============================================
-- ЧАСТЬ 7: ОПТИМИЗАЦИЯ И ЛУЧШИЕ ПРАКТИКИ
-- ============================================

-- 1. Используйте PARTITION BY для уменьшения размера окна
-- 2. ORDER BY должен использовать индексированные колонки
-- 3. Избегайте оконных функций в WHERE (используйте подзапросы)
-- 4. Используйте именованные окна для повторяющихся определений

-- Пример именованного окна:
SELECT 
    name,
    salary,
    RANK() OVER w AS salary_rank,
    DENSE_RANK() OVER w AS salary_dense_rank,
    PERCENT_RANK() OVER w AS salary_percentile
FROM employees
WINDOW w AS (ORDER BY salary DESC);

-- ============================================
-- ЧАСТЬ 8: ЧАСТЫЕ ОШИБКИ И РЕШЕНИЯ
-- ============================================

-- ОШИБКА 1: Использование оконной функции в WHERE
-- НЕПРАВИЛЬНО:
-- SELECT name, salary, RANK() OVER (ORDER BY salary) AS rn
-- FROM employees
-- WHERE rn <= 3;  -- Ошибка!

-- ПРАВИЛЬНО:
-- SELECT name, salary, rn
-- FROM (
--     SELECT name, salary, RANK() OVER (ORDER BY salary) AS rn
--     FROM employees
-- ) AS ranked
-- WHERE rn <= 3;

-- ОШИБКА 2: Забыли ORDER BY в LAST_VALUE
-- НЕПРАВИЛЬНО:
-- LAST_VALUE(sales) OVER (PARTITION BY department)  -- Неправильно!

-- ПРАВИЛЬНО:
-- LAST_VALUE(sales) OVER (
--     PARTITION BY department 
--     ORDER BY date
--     ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
-- )

-- ОШИБКА 3: Неправильное использование RANGE vs ROWS
-- ROWS - физические строки
-- RANGE - логические значения (может включать несколько строк с одинаковыми значениями)

-- ============================================
-- ЧАСТЬ 9: ПРАКТИЧЕСКИЕ ЗАДАЧИ ДЛЯ ТРЕНИРОВКИ
-- ============================================

-- Задача 1: Найти сотрудников с зарплатой выше средней по отделу
SELECT 
    name,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg
FROM employees
WHERE salary > AVG(salary) OVER (PARTITION BY department);  -- Ошибка! Нужен подзапрос

-- Правильное решение:
SELECT name, department, salary, dept_avg
FROM (
    SELECT 
        name,
        department,
        salary,
        AVG(salary) OVER (PARTITION BY department) AS dept_avg
    FROM employees
) AS ranked
WHERE salary > dept_avg;

-- Задача 2: Найти разницу между максимальной и минимальной зарплатой в каждом отделе
SELECT 
    department,
    MAX(salary) OVER (PARTITION BY department) - 
    MIN(salary) OVER (PARTITION BY department) AS salary_range
FROM employees
GROUP BY department, salary;  -- Неправильно!

-- Правильное решение:
SELECT DISTINCT
    department,
    MAX(salary) OVER (PARTITION BY department) - 
    MIN(salary) OVER (PARTITION BY department) AS salary_range
FROM employees;

-- Задача 3: Найти сотрудников, которые получают больше, чем предыдущий сотрудник
SELECT 
    name,
    salary,
    LAG(salary) OVER (ORDER BY salary) AS prev_salary
FROM employees
WHERE salary > LAG(salary) OVER (ORDER BY salary);  -- Ошибка!

-- Правильное решение:
SELECT name, salary, prev_salary
FROM (
    SELECT 
        name,
        salary,
        LAG(salary) OVER (ORDER BY salary) AS prev_salary
    FROM employees
) AS compared
WHERE salary > prev_salary;

-- ============================================
-- ЧАСТЬ 10: ПРОИЗВОДИТЕЛЬНОСТЬ
-- ============================================

-- Оконные функции обычно быстрее подзапросов:
-- МЕДЛЕННО (подзапрос):
-- SELECT 
--     e1.name,
--     e1.salary,
--     (SELECT AVG(salary) FROM employees e2 WHERE e2.department = e1.department) AS dept_avg
-- FROM employees e1;

-- БЫСТРО (оконная функция):
-- SELECT 
--     name,
--     salary,
--     AVG(salary) OVER (PARTITION BY department) AS dept_avg
-- FROM employees;

-- ============================================
-- КОНЕЦ РУКОВОДСТВА
-- ============================================
