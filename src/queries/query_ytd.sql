SELECT
  g.ga4_date,

  -- kpi de sessions
  g.sessions_a1 AS sessions_j,
  g.sessions_a1_n1 AS sessions_j7,
  g.evol_sessions_a1_n1 AS evol_sessions_jj7,

    -- kpi sessions avec cart view
  g.cart_page_session_view_a1 AS cart_page_session_view_j,
  g.cart_page_session_view_a1_n1 AS cart_page_session_view_j7,
  g.evol_cart_page_session_view_a1_n1 AS evol_cart_page_session_view_jj7,

  -- kpi sessions avec purchase
  g.session_purchase_a1 AS session_purchase_j,
  g.session_purchase_a1_n1 AS session_purchase_j7,
  g.evol_session_purchase_a1_n1 AS evol_session_purchase_jj7,

  -- kpi de conversion
  g.conversions_a1 AS conversions_j,
  g.conversions_a1_n1 AS conversions_j7,
  g.evol_conversions_a1_n1 AS evol_conversions_jj7,

    -- kpi de perf abonnement total
  p.abo_a1 AS abo_j,
  p.abo_a1_n1 AS abo_j_n1,
  p.evol_abo_a1_n1 AS evol_abo_j_n1,
  p.target_abo_a1 AS target_abo_j,

-- kpi de perf abonnement print
  p.abo_print_a1 AS abo_print_j,
  p.abo_print_a1_n1 AS abo_print_j_n1,
  p.evol_abo_print_a1_n1 AS evol_abo_print_j_n1,
  p.target_abo_print_a1 AS target_abo_print_j,

-- kpi de perf abonnement numérique
  p.abo_num_a1 AS abo_num_j,
  p.abo_num_a1_n1 AS abo_num_j_n1,
  p.evol_abo_num_a1_n1 AS evol_abo_num_j_n1,
  p.target_abo_num_a1 AS target_abo_num_j,

-- kpi de perf réabo
  p.reabo_a1 AS reabo_j,
  p.reabo_a1_n1 AS reabo_j_n1,
  p.evol_reabo_a1_n1 AS evol_reabo_j_n1,
  p.target_reabo_a1 AS target_reabo_j,

-- kpi de vente au numéro
  p.van_a1 AS van_j,
  p.van_a1_n1 AS van_j_n1,
  p.evol_van_a1_n1 AS evol_van_j_n1,
  p.target_van_a1 AS target_van_j,

-- kpi vad
  p.vad_a1 AS vad_j,
  p.vad_a1_n1 AS vad_j_n1,
  p.evol_vad_a1_n1 AS evol_vad_j_n1,
  p.target_vad_a1 AS target_vad_j,

-- kpi marketplace
  p.marketplace_a1 AS marketplace_j,
  p.marketplace_a1_n1 AS marketplace_j_n1,
  p.evol_marketplace_a1_n1 AS evol_marketplace_j_n1,
  p.target_marketplace_a1 AS target_marketplace_j

FROM `{dataset}.ga4_mail_daily` AS g

LEFT JOIN `{dataset}.perf_mail_daily` AS p
  ON p.perf_date = DATE_ADD(g.ga4_date, INTERVAL 1 DAY)

WHERE g.ga4_date = "{report_date_minus1}"