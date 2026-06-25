SELECT
  g.ga4_date,

  -- kpi de sessions
  g.sessions_j,
  g.sessions_j7,
  g.evol_sessions_jj7,

  -- kpi sessions avec cart view
  g.cart_page_session_view_j,
  g.cart_page_session_view_j7,
  g.evol_cart_page_session_view_jj7,

  -- kpi sessions avec purchase
  g.session_purchase_j,
  g.session_purchase_j7,
  g.evol_session_purchase_jj7,

  -- kpi de conversion
  g_plus1.conversions_j,
  g_plus1.conversions_j7,
  g_plus1.evol_conversions_jj7,

  -- kpi de perf abonnement total
  p.abo_j,
  p.abo_j_n1,
  p.evol_abo_j_n1,
  p.target_abo_j,

-- kpi de perf abonnement print
  p.abo_print_j,
  p.abo_print_j_n1,
  p.evol_abo_print_j_n1,
  p.target_abo_print_j,

-- kpi de perf abonnement numérique
  p.abo_num_j,
  p.abo_num_j_n1,
  p.evol_abo_num_j_n1,
  p.target_abo_num_j,

-- kpi de perf réabo
  p.reabo_j,
  p.reabo_j_n1,
  p.evol_reabo_j_n1,
  p.target_reabo_j,

-- kpi de vente au numéro
  p.van_j,
  p.van_j_n1,
  p.evol_van_j_n1,
  p.target_van_j,

-- kpi vad
  p.vad_j,
  p.vad_j_n1,
  p.evol_vad_j_n1,
  p.target_vad_j,

-- kpi marketplace
  p.marketplace_j,
  p.marketplace_j_n1,
  p.evol_marketplace_j_n1,
  p.target_marketplace_j


FROM `{dataset}.ga4_mail_daily` AS g

LEFT JOIN `{dataset}.ga4_mail_daily` AS g_plus1
  ON g_plus1.ga4_date = DATE_ADD(g.ga4_date, INTERVAL 1 DAY)

LEFT JOIN `{dataset}.perf_mail_daily` AS p
  ON p.perf_date = DATE_ADD(g.ga4_date, INTERVAL 1 DAY)

WHERE g.ga4_date = "{report_date_minus1}"