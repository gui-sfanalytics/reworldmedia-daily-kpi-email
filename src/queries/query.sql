SELECT
  g.ga4_date,

  -- kpi de sessions
  g.sessions_j,
  g.sessions_j7,
  g.evol_sessions_jj7,

  -- kpi de add_to_cart
  g.add_to_cart_j,
  g.add_to_cart_j7,
  g.evol_add_to_cart_jj7,

  -- kpi sessions avec cart view
  g.cart_page_session_view_j,
  g.cart_page_session_view_j7,
  g.evol_cart_page_session_view_jj7,

  -- kpi sessions avec purchase
  g.session_purchase_j,
  g.session_purchase_j7,
  g.evol_session_purchase_jj7,

  -- kpi de conversions
  g.conversions_j,
  g.conversions_j7,
  g.evol_conversions_jj7,

  -- kpi de perf abonnement total
  p.abo_j,
  p.abo_j7,
  p.evol_abo_jj7,
  p.target_abo_j,

-- kpi de perf abonnement print
  p.abo_print_j,
  p.abo_print_j7,
  p.evol_abo_print_jj7,
  p.target_abo_print_j,

-- kpi de perf réabo
  p.reabo_j,
  p.reabo_j7,
  p.evol_reabo_jj7,
  p.target_reabo_j,

-- kpi de vente au numéro
  p.van_j,
  p.van_j7,
  p.evol_van_jj7,
  p.target_van_j,

-- kpi vad
  p.vad_j,
  p.vad_j7,
  p.evol_vad_jj7,
  p.target_vad_j

FROM `reporting.ga4_mail_daily` AS g

LEFT JOIN `reporting.perf_mail_daily` AS p
  ON p.perf_date = g.ga4_date

WHERE g.ga4_date = '2026-05-10';