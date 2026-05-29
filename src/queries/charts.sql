SELECT
    perf_month,
    abo_m,
    abo_m_n1,
    abo_ytd,
    abo_ytd_n1,
    target_total_month,
    target_total_ytd
FROM reporting.perf_mail_monthly
WHERE perf_month BETWEEN 
  DATE_SUB(
    DATE_TRUNC(PARSE_DATE('%Y-%m-%d', '{report_date}'), MONTH),
    INTERVAL 11 MONTH
  )
  AND DATE_TRUNC(PARSE_DATE('%Y-%m-%d', '{report_date}'), MONTH)
ORDER BY perf_month 