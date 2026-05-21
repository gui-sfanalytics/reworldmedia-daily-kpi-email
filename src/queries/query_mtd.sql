SELECT
  g.ga4_date,

  -- kpi de sessions
  g.sessions_m1 AS sessions_j,
  g.sessions_m1j7 AS sessions_j7,
  g.evol_sessions_m1j7 AS evol_sessions_jj7,

  -- kpi de add_to_cart
  g.add_to_cart_m1 AS add_to_cart_j,
  g.add_to_cart_m1j7 AS add_to_cart_j7,
  g.evol_add_to_cart_m1j7 AS evol_add_to_cart_jj7,

  -- kpi sessions avec cart view
  g.cart_page_session_view_m1 AS cart_page_session_view_j,
  g.cart_page_session_view_m1j7 AS cart_page_session_view_j7,
  g.evol_cart_page_session_view_m1j7 AS evol_cart_page_session_view_jj7,

  -- kpi sessions avec purchase
  g.session_purchase_m1 AS session_purchase_j,
  g.session_purchase_m1j7 AS session_purchase_j7,
  g.evol_session_purchase_m1j7 AS evol_session_purchase_jj7,

  -- kpi de conversions
  g.conversion_m1 AS conversions_j,
  g.conversion_m1j7 AS conversions_j7,
  g.evol_conversion_m1j7 AS evol_conversions_jj7,

  -- kpi de perf abonnement total
  p.abo_m1 AS abo_j,
  p.abo_m1j7 AS abo_j7,
  p.evol_abo_m1j7 AS evol_abo_jj7,
  p.target_abo_m1 AS target_abo_j,

-- kpi de perf abonnement print
  p.abo_print_m1 AS abo_print_j,
  p.abo_print_m1j7 AS abo_print_j7,
  p.evol_abo_print_m1j7 AS evol_abo_print_jj7,
  p.target_abo_print_m1 AS target_abo_print_j,

-- kpi de perf réabo
  p.reabo_m1 AS reabo_j,
  p.reabo_m1j7 AS reabo_j7,
  p.evol_reabo_m1j7 AS evol_reabo_jj7,
  p.target_reabo_m1 AS target_reabo_j,

-- kpi de vente au numéro
  p.van_m1 AS van_j,
  p.van_m1j7 AS van_j7,
  p.evol_van_m1j7 AS evol_van_jj7,
  p.target_van_m1 AS target_van_j,

-- kpi vad
  p.vad_m1 AS vad_j,
  p.vad_m1j7 AS vad_j7,
  p.evol_vad_m1j7 AS evol_vad_jj7,
  p.target_vad_m1 AS target_vad_j

FROM `reporting.ga4_mail_daily` AS g

LEFT JOIN `reporting.perf_mail_daily` AS p
  ON p.perf_date = g.ga4_date

WHERE g.ga4_date = '2026-05-10';