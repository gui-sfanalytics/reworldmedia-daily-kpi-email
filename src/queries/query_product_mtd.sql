SELECT
  p.prod_date,
  p.titre,

  -- KPI j
p.abo_m1 AS abo_j,
p.abo_m1_n1 AS abo_j_n1,
p.evol_abo_m1_n1 AS evol_abo_j_n1,
p.target_abo_m1 AS target_abo_j


FROM `{dataset}.product_mail_daily` AS p
    
WHERE p.prod_date = "{report_date}"

ORDER BY p.abo_m1 DESC
LIMIT 5;