SELECT
  p.prod_date,
  p.titre,

  -- KPI j
p.abo_j,
p.abo_j_n1,
p.evol_abo_j_n1,
p.target_abo_j


FROM `{dataset}.product_mail_daily` AS p
    
WHERE p.prod_date = "{report_date}"

ORDER BY p.abo_j DESC
LIMIT 5;