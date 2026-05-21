SELECT
  p.prod_date,
  p.titre,

  -- KPI j
p.abo_j,
p.abo_j7,
p.evol_abo_jj7,
p.target_abo_j


FROM `reporting.product_mail_daily` AS p
    
WHERE p.prod_date = '2026-05-10'

ORDER BY p.abo_j DESC
LIMIT 5;