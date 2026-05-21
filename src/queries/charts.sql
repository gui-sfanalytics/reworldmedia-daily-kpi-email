SELECT
    perf_month,
    abo_m,
    abo_m_n1,
    abo_ytd,
    abo_ytd_n1,
    target_total_month,
    target_total_ytd
FROM reporting.perf_mail_monthly
---WHERE perf_month >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
WHERE perf_month BETWEEN DATE('2025-06-01') AND DATE('2026-05-01')
ORDER BY perf_month