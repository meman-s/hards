SELECT
    id,
    user_id,
    amount,
    paid_at,
    sum(amount) over (
        PARTITION BY user_id
        ORDER BY
            paid_at ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
    ) as user_summ,
    rank() over (
        PARTITION BY user_id
        ORDER BY
            paid_at
    )
from
    payments;