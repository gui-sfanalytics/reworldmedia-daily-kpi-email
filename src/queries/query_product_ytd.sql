SELECT
  p.prod_date,
  p.titre,

  -- KPI j
p.abo_a1 AS abo_j,
p.abo_a1_n1 AS abo_j_n1,
p.evol_abo_a1_n1 AS evol_abo_j_n1,
p.target_abo_a1 AS target_abo_j


FROM `reporting.product_mail_daily` AS p
    
WHERE p.prod_date = "{report_date}"

ORDER BY p.abo_a1 DESC
LIMIT 5;