def calcul_data(db_value):

    def evol_decorator(value):
        return f"{value:+g}"
    
    def evol_decorator_p(value):
        return f"{round(value, 2):+g}%"
    
    def thousand_separator(value):
        return f"{int(value):,}".replace(",", " ")

    def color_class(value):
        return "positive" if value >= 0 else "negative"

    def text_color_class(value):
        return "positive-text" if value >= 0 else "negative-text"

    sessions_delta_value = round(db_value["evol_sessions_jj7"], 2)
    conversions_delta_value = round(db_value["evol_conversions_jj7"], 2)
    conversion_rate_delta_value = round((db_value["conversions_j"] / db_value["sessions_j"])*100, 2) - round((db_value["conversions_j7"] / db_value["sessions_j7"])*100, 2)
    add_to_cart_delta_value = round(db_value["evol_add_to_cart_jj7"], 2)
    add_to_cart_rate_delta_value = round((db_value["add_to_cart_j"] / db_value["sessions_j"])*100, 2) - round((db_value["add_to_cart_j7"] / db_value["sessions_j7"])*100, 2)
    checkout_completion_rate_delta_value = round((db_value["session_purchase_j"] / db_value["cart_page_session_view_j"])*100, 2) - round((db_value["session_purchase_j7"] / db_value["cart_page_session_view_j7"])*100, 2)

    kpis_web = {
        "sessions": thousand_separator(db_value["sessions_j"]),
        "sessions_previous": thousand_separator(db_value["sessions_j7"]),
        "sessions_delta_value": sessions_delta_value,
        "sessions_delta": evol_decorator_p(sessions_delta_value),
        "sessions_delta_class": color_class(sessions_delta_value),
        "sessions_delta_text_class": text_color_class(sessions_delta_value),

        "conversions": thousand_separator(db_value["session_purchase_j"]),
        "conversions_previous": thousand_separator(db_value["session_purchase_j7"]),
        "conversions_delta_value": conversions_delta_value,
        "conversions_delta": evol_decorator_p(conversions_delta_value),
        "conversions_delta_class": color_class(conversions_delta_value),
        "conversions_delta_text_class": text_color_class(conversions_delta_value),

        "conversion_rate": str(round((db_value["conversions_j"] / db_value["sessions_j"])*100, 2)) + "%",
        "conversion_rate_previous": str(round((db_value["conversions_j7"] / db_value["sessions_j7"])*100, 2)) + "%",
        "conversion_rate_delta_value": conversion_rate_delta_value,
        "conversion_rate_delta": evol_decorator(conversion_rate_delta_value),
        "conversion_rate_delta_class": color_class(conversion_rate_delta_value),
        "conversion_rate_delta_text_class": text_color_class(conversion_rate_delta_value),

        "add_to_cart": thousand_separator(db_value["add_to_cart_j"]),
        "add_to_cart_previous": thousand_separator(db_value["add_to_cart_j7"]),
        "add_to_cart_delta_value": add_to_cart_delta_value,
        "add_to_cart_delta": evol_decorator_p(add_to_cart_delta_value),
        "add_to_cart_delta_class": color_class(add_to_cart_delta_value),
        "add_to_cart_delta_text_class": text_color_class(add_to_cart_delta_value),

        "add_to_cart_rate": str(round((db_value["add_to_cart_j"] / db_value["sessions_j"])*100, 2)) + "%",
        "add_to_cart_rate_previous": str(round((db_value["add_to_cart_j7"] / db_value["sessions_j7"])*100, 2)) + "%",
        "add_to_cart_rate_delta_value": add_to_cart_rate_delta_value,
        "add_to_cart_rate_delta": evol_decorator(add_to_cart_rate_delta_value),
        "add_to_cart_rate_delta_class": color_class(add_to_cart_rate_delta_value),
        "add_to_cart_rate_delta_text_class": text_color_class(add_to_cart_rate_delta_value),

        "checkout_completion_rate": str(round((db_value["session_purchase_j"] / db_value["cart_page_session_view_j"])*100, 2)) + "%",
        "checkout_completion_rate_previous": str(round((db_value["session_purchase_j7"] / db_value["cart_page_session_view_j7"])*100, 2)) + "%",
        "checkout_completion_rate_delta_value": checkout_completion_rate_delta_value,
        "checkout_completion_rate_delta": evol_decorator(checkout_completion_rate_delta_value),
        "checkout_completion_rate_delta_class": color_class(checkout_completion_rate_delta_value),
        "checkout_completion_rate_delta_text_class": text_color_class(checkout_completion_rate_delta_value),
    }

    performance_kpis = [
        {
            "label": "Abo Vs (N-1)",
            "current": thousand_separator(db_value["abo_j"]),
            "current_value": db_value["abo_j"],
            "previous": thousand_separator(db_value["abo_j7"]),
            "delta_percent": db_value["evol_abo_jj7"],
            "target": thousand_separator(db_value["target_abo_j"]),
            "target_value": db_value["target_abo_j"],
            "budget_label": "Abo Vs Budget",
        },
        {
            "label": "Abo Print Vs (N-1)",
            "current": thousand_separator(db_value["abo_print_j"]),
            "current_value": db_value["abo_print_j"],
            "previous": thousand_separator(db_value["abo_print_j7"]),
            "delta_percent": db_value["evol_abo_print_jj7"],
            "target": thousand_separator(db_value["target_abo_print_j"]),
            "target_value": db_value["target_abo_print_j"],
            "budget_label": "Abo Print Vs Budget",
        },
        {
            "label": "Réabo Vs (N-1)",
            "current": thousand_separator(db_value["reabo_j"]),
            "current_value": db_value["reabo_j"],
            "previous": thousand_separator(db_value["reabo_j7"]),
            "delta_percent": db_value["evol_reabo_jj7"],
            "target": thousand_separator(db_value["target_reabo_j"]),
            "target_value": db_value["target_reabo_j"],
            "budget_label": "Réabo Vs Budget",
        },
        {
            "label": "Abo + Reabo Vs (N-1)",
            "current": thousand_separator(db_value["abo_j"] + db_value["reabo_j"]),
            "current_value": db_value["abo_j"] + db_value["reabo_j"],
            "previous": thousand_separator(str(int(db_value["abo_j7"] + db_value["reabo_j7"]))),
            "delta_percent": db_value["evol_abo_jj7"] if db_value["evol_abo_jj7"] == db_value["evol_reabo_jj7"] else (db_value["evol_abo_jj7"] + db_value["evol_reabo_jj7"]) / 2,
            "target": thousand_separator(db_value["target_abo_j"] + db_value["target_reabo_j"]),
            "target_value": db_value["target_abo_j"] + db_value["target_reabo_j"],
            "budget_label": "Abo+Reabo Vs Budget",
        },
        {
            "label": "Total VAN Vs (N-1)",
            "current": thousand_separator(db_value["van_j"]),
            "current_value": db_value["van_j"],
            "previous": thousand_separator(str(int(db_value["van_j7"]))),
            "delta_percent": db_value["evol_van_jj7"],
            "target": thousand_separator(db_value["target_van_j"]),
            "target_value": db_value["target_van_j"],
            "budget_label": "VAN Vs Budget",
        },
        {
            "label": "VAD Vs (N-1)",
            "current": thousand_separator(db_value["vad_j"]),
            "current_value": db_value["vad_j"],
            "previous": thousand_separator(str(int(db_value["vad_j7"]))),
            "delta_percent": db_value["evol_vad_jj7"],
            "target": thousand_separator(db_value["target_vad_j"]),
            "target_value": db_value["target_vad_j"],
            "budget_label": "VAD Vs Budget",
        },
    ]

    return kpis_web, performance_kpis

def calcul_data_product(db_value):

    top_subscriptions = []

    for row in db_value:

        product = dict(row)

        product["product_name"] = product["titre"]
        product["current"] = int(product["abo_j"] or 0)
        product["previous"] = int(product["abo_j7"] or 0)
        product["delta_percent"] = int(product["evol_abo_jj7"] or 0)
        product["target"] = int(product["target_abo_j"] or 0)

        top_subscriptions.append(product)

    return top_subscriptions