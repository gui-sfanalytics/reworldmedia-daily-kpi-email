import sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
from werkzeug.exceptions import HTTPException

import os

from jinja2 import Environment, FileSystemLoader
from matplotlib import dates
from playwright.sync_api import sync_playwright
from flask import Flask

import base64
import requests

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from google.cloud import bigquery
from google.cloud import storage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth import default
credentials, project = default()
from google.auth import iam

import google.cloud.storage

from src.data import calcul_data, calcul_data_product
from templates.full_mail import build_mail_html
from src.charts import create_subscription_charts

from datetime import datetime, timedelta

import traceback
from flask import jsonify
from flask import request

ENV = os.getenv("ENV", "local") 
HTML_OUTPUT_DIR = "src/outputs/html"
PNG_OUTPUT_DIR = "src/outputs/png"
SQL_DIR = "src/queries"
os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)
os.makedirs(PNG_OUTPUT_DIR, exist_ok=True)
os.makedirs(SQL_DIR, exist_ok=True)

print("STORAGE VERSION:", google.cloud.storage.__version__)

# -----------------------------
# manipulation dates
# -----------------------------

def get_same_weekday_last_year(date_obj):
    iso_year, iso_week, iso_weekday = date_obj.isocalendar()
    target_year = iso_year - 1
    first_day = datetime.strptime(f"{target_year}-W{iso_week:02d}-1", "%G-W%V-%u")
    return first_day + timedelta(days=iso_weekday - 1)

def main_process(report_date):
    print(f"Process started for {report_date}")

    def compute_dates(date_str):
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")

        same_weekday_last_year = get_same_weekday_last_year(date_obj)

        same_day_last_year = date_obj.replace(year=date_obj.year - 1)

        first_day_month = date_obj.replace(day=1)
        first_day_month_last_year = first_day_month.replace(year=date_obj.year - 1)

        first_day_year = date_obj.replace(month=1, day=1)
        first_day_year_last_year = first_day_year.replace(year=date_obj.year - 1)

        return {
            "report_day": date_obj.strftime("%d/%m/%Y"),
            "report_day_sql": date_obj.strftime("%Y-%m-%d"),
            "same_weekday_last_year": same_weekday_last_year.strftime("%d/%m/%Y"),
            "same_day_last_year": same_day_last_year.strftime("%d/%m/%Y"),
            "first_day_month": first_day_month.strftime("%d/%m/%Y"),
            "first_day_month_last_year": first_day_month_last_year.strftime("%d/%m/%Y"),
            "first_day_year": first_day_year.strftime("%d/%m/%Y"),
            "first_day_year_last_year": first_day_year_last_year.strftime("%d/%m/%Y"),
            "first_day_year_last_year_sql": first_day_year_last_year.strftime("%Y-%m-%d"),
        }

    # -----------------------------
    # PNG GENERATION
    # -----------------------------

    def html_to_png(html_path, png_path, width=640, height=520):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            page = browser.new_page(
                viewport={
                    "width": width,
                    "height": height,
                }
            )

            page.goto("file://" + os.path.abspath(html_path))

            page.screenshot(
                path=png_path,
                full_page=True
            )

            browser.close()

            print("PNG generated : " + png_path)

    # -----------------------------
    # BIGQUERY
    # -----------------------------

    run_date_folder = datetime.strptime(report_date, "%d/%m/%Y").strftime("%Y-%m-%d")

    def upload_to_gcs(local_file_path, bucket_name, destination_blob_name):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)

        if ENV == "local":
            print(f"  [LOCAL] Upload OK → gs://{bucket_name}/{destination_blob_name} (pas de signed URL)")
            return f"gs://{bucket_name}/{destination_blob_name}"  # non utilisée en local (cid: utilisés)

        else:
            # En GCP : service account → signed URL
            credentials, project_id = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            credentials.refresh(Request())

            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET",
                service_account_email=credentials.service_account_email,
                access_token=credentials.token,
            )
            return url

    # -----------------------------
    # Génère une signed URL pour un blob GCS déjà existant (sans re-upload)
    # -----------------------------

    def get_gcs_signed_url(bucket_name, blob_name):
        if ENV == "local":
            # Non appelée en local normalement, mais sécurité
            return f"gs://{bucket_name}/{blob_name}"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET",
            service_account_email=credentials.service_account_email,
            access_token=credentials.token,
        )
        return url

    client = bigquery.Client()

    env = Environment(
        loader=FileSystemLoader("templates")
    )

    # -----------------------------
    # Appel des queries
    # -----------------------------

    def generate_period_report(period_name, query_file, product_query_file, report_title, current_date, previous_date):

        report_date_minus1 = (datetime.strptime(report_date, "%d/%m/%Y") - timedelta(days=1)).strftime("%Y-%m-%d")

        with open(SQL_DIR + "/" + query_file, "r", encoding="utf-8") as f:
            query = f.read().format(report_date=dates['report_day_sql'], report_date_minus1=report_date_minus1)

        query_job = client.query(query)
        rows = list(query_job.result())

        if not rows:
            raise ValueError(
                f"Aucune donnée retournée pour {period_name} avec {query_file}"
            )

        row = rows[0]

        kpis_web, performance_kpis = calcul_data(row)

        for kpi in performance_kpis:
            achievement = ((kpi["current_value"] / kpi["target_value"]) - 1) * 100 if kpi["target_value"] else 0
            kpi["achievement_percent"] = achievement
            kpi["achievement_display"] = f"{achievement:+.0f}%"
            kpi["delta_display"] = f"{kpi['delta_percent']:+.1f}%"

            max_value = max(kpi["current_value"], kpi["target_value"]) * 1.08 if max(kpi["current_value"], kpi["target_value"]) else 1
            kpi["current_percent_clamped"] = min(100, max(0, round(kpi["current_value"] / max_value * 100, 1)))
            kpi["target_percent_clamped"] = min(100, max(0, round(kpi["target_value"] / max_value * 100, 1)))

        with open( SQL_DIR + "/" + product_query_file, "r", encoding="utf-8") as f:
            query = f.read().format(report_date=dates['report_day_sql'])

        query_job = client.query(query)
        rows = list(query_job.result())
        top_subscriptions = calcul_data_product(rows)

        for product in top_subscriptions:
            achievement = ((product["current"] / product["target"]) - 1) * 100 if product["target"] else 0
            product["achievement_percent"] = achievement
            product["achievement_display"] = f"{achievement:+.0f}%"
            product["delta_display"] = f"{product['delta_percent']:+.0f}%"

            max_value = max(product["current"], product["target"]) * 1.08 if max(product["current"], product["target"]) else 1
            product["current_percent_clamped"] = min(100, max(0, round(product["current"] / max_value * 100, 1)))
            product["target_percent_clamped"] = min(100, max(0, round(product["target"] / max_value * 100, 1)))

        ## generation des templates
        ## KPI Web
        template = env.get_template("kpi_web.html")
        html_content = template.render(**kpis_web,
                                    report_title=report_title,
                                        current_date=current_date,
                                        previous_date=previous_date,
                                        report_date=dates['report_day_sql'],
                                        )

        html_file = f"{HTML_OUTPUT_DIR}/{period_name}_kpi_web.html"
        png_file = f"{PNG_OUTPUT_DIR}/{period_name}_kpi_web.png"

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        html_to_png(html_file, png_file, width=720, height=250)

        png_url = upload_to_gcs(
            png_file,
            "kpi-email-storage",
            f"{run_date_folder}/{os.path.basename(png_file)}"
        )
        image_urls[f"{period_name}_kpi_web"] = png_url

        ## Performance indicators
        template_perf = env.get_template("performance_indicators.html")
        html_perf = template_perf.render(**kpis_web,
                                        performance_kpis=performance_kpis,
                                        report_title=report_title,
                                        current_date=current_date,
                                        previous_date=previous_date,
                                        report_date=dates['report_day_sql'],
                                        period_name=period_name)

        html_file = f"{HTML_OUTPUT_DIR}/{period_name}_performance_indicators.html"
        png_file = f"{PNG_OUTPUT_DIR}/{period_name}_performance_indicators.png"

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_perf)

        html_to_png(html_file, png_file, width=720, height=560)

        png_url = upload_to_gcs(
            png_file,
            "kpi-email-storage",
            f"{run_date_folder}/{os.path.basename(png_file)}"
        )
        image_urls[f"{period_name}_performance_indicators"] = png_url

        template_top = env.get_template("top_subscriptions.html")
        html_top = template_top.render(top_subscriptions=top_subscriptions,
                                    report_title=report_title,
                                        current_date=current_date,
                                        previous_date=previous_date)

        html_file = f"{HTML_OUTPUT_DIR}/{period_name}_top_subscriptions.html"
        png_file = f"{PNG_OUTPUT_DIR}/{period_name}_top_subscriptions.png"

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_top)

        html_to_png(html_file, png_file, width=720, height=630)

        png_url = upload_to_gcs(
            png_file,
            "kpi-email-storage",
            f"{run_date_folder}/{os.path.basename(png_file)}"
        )
        image_urls[f"{period_name}_top_subscriptions"] = png_url

    def get_subscription_chart_data():
        with open(os.path.join(SQL_DIR, "charts.sql"), "r", encoding="utf-8") as f:
            query = f.read().format(report_date=dates['report_day_sql'], start_date=dates['first_day_year_last_year_sql'])

        rows = list(client.query(query).result())

        months = []
        abo_m = []
        abo_m_n1 = []
        abo_ytd = []
        abo_ytd_n1 = []
        target_month = []
        target_ytd = []

        month_labels = {
            1: "janv.",
            2: "févr.",
            3: "mars",
            4: "avr.",
            5: "mai",
            6: "juin",
            7: "juil.",
            8: "août",
            9: "sept",
            10: "oct",
            11: "nov",
            12: "déc.",
        }

        for row in rows:
            months.append(month_labels[row.perf_month.month])
            abo_m.append(row.abo_m or 0)
            abo_m_n1.append(row.abo_m_n1 or 0)
            abo_ytd.append(row.abo_ytd or 0)
            abo_ytd_n1.append(row.abo_ytd_n1 or 0)
            target_month.append(row.target_total_month or 0)
            target_ytd.append(row.target_total_ytd or 0)

        current_year = datetime.strptime(dates['report_day_sql'], "%Y-%m-%d").year

        months_ytd = []
        abo_ytd_filtered = []
        abo_ytd_n1_filtered = []
        target_ytd_filtered = []

        for i, row in enumerate(rows):
            if row.perf_month.year == current_year:
                months_ytd.append(months[i])
                abo_ytd_filtered.append(abo_ytd[i])
                abo_ytd_n1_filtered.append(abo_ytd_n1[i])
                target_ytd_filtered.append(target_ytd[i])

        return {
            "months": months,
            "sliding_year": abo_m,
            "sliding_year_n1": abo_m_n1,
            "objectifs": target_month,
            "consolidated": abo_ytd_filtered,
            "consolidated_n1": abo_ytd_n1_filtered,
            "consolidated_obj": target_ytd_filtered,
            "months_ytd": months_ytd,
        }

    dates = compute_dates(report_date)
    image_urls = {}

    # ── Détection du 2 du mois ────────────────────────────────────────────────
    date_obj = datetime.strptime(report_date, "%d/%m/%Y")
    is_month_recap = (date_obj.day == 1)
    mtd_folder = (date_obj - timedelta(days=1)).strftime("%Y-%m-%d") if is_month_recap else run_date_folder

    generate_period_report(
        "daily",
        "query.sql",
        "query_product.sql",
        "Jour",
        dates["report_day"],
        dates["same_weekday_last_year"]
    )

    generate_period_report(
        "mtd",
        "query_mtd.sql",
        "query_product_mtd.sql",
        "Mois à mois",
        f"{dates['first_day_month']} au {dates['report_day']}",
        f"{dates['first_day_month_last_year']} au {dates['same_day_last_year']}"
    )

    generate_period_report(
        "ytd",
        "query_ytd.sql",
        "query_product_ytd.sql",
        "Année à année",
        f"{dates['first_day_year']} au {dates['report_day']}",
        f"{dates['first_day_year_last_year']} au {dates['same_day_last_year']}"
    )

    # ── Remplacement des URLs MTD si on est le 2 du mois ─────────────────────
    if is_month_recap:
        print(f"[MONTH RECAP] Remplacement des URLs MTD → dossier {mtd_folder}")
        mtd_keys = ["mtd_kpi_web"]

        if ENV == "local":
            # En local : télécharger le PNG de la veille depuis GCS
            storage_client = storage.Client()
            for key in mtd_keys:
                blob_name = f"{mtd_folder}/{key}.png"
                local_path = f"{PNG_OUTPUT_DIR}/{key}.png"
                try:
                    bucket = storage_client.bucket("kpi-email-storage")
                    blob = bucket.blob(blob_name)
                    blob.download_to_filename(local_path)
                    print(f"  ✓ {key} téléchargé depuis gs://kpi-email-storage/{blob_name} → {local_path}")
                except Exception as e:
                    print(f"  ⚠️ Impossible de télécharger {blob_name} : {e} — PNG du jour conservé")
        else:
            # En GCP : remplacer par signed URL
            for key in mtd_keys:
                blob_name = f"{mtd_folder}/{key}.png"
                try:
                    image_urls[key] = get_gcs_signed_url("kpi-email-storage", blob_name)
                    print(f"  ✓ {key} → gs://kpi-email-storage/{blob_name}")
                except Exception as e:
                    print(f"  ⚠️ Impossible de récupérer {blob_name} : {e} — URL du jour conservée")

    ## generation des charts d'évolution des abonnements 
    charts_path = os.path.join(PNG_OUTPUT_DIR, "subscription_charts.png")
    chart_data = get_subscription_chart_data()
    create_subscription_charts(
        output_path=charts_path,
        **chart_data
    )

    chart_url = upload_to_gcs(
        charts_path,
        "kpi-email-storage",
        f"{run_date_folder}/subscription_charts.png"
    )

    image_urls["subscription_charts"] = chart_url

    # -----------------------------
    # setup email
    # -----------------------------

    def get_recipients():
        client = bigquery.Client()

        query = """
        SELECT email, type
        FROM `reporting.email_recipients`
        WHERE actif = TRUE
        """

        rows = client.query(query).result()

        to_list = []
        cc_list = []
        bcc_list = []

        for row in rows:
            if row.type == "to":
                to_list.append(row.email)
            elif row.type == "cc":
                cc_list.append(row.email)
            elif row.type == "bcc":
                bcc_list.append(row.email)

        return to_list, cc_list, bcc_list

    def send_email_n8n(html):
        url = "https://app.starfox-analytics.com/webhook/gmail-send-html"

        to_list, cc_list, bcc_list = get_recipients()

        payload = {
            "to": ",".join(to_list),
            "cc": ",".join(cc_list),
            "bcc": ",".join(bcc_list),
            "subject": "Reporting Quotidien ReworldMedia",
            "html": html
        }

        response = requests.post(url, json=payload)

        print("n8n:", response.status_code, response.text)

        if response.status_code >= 300:
            raise Exception("Email failed via n8n")

    if ENV == "local":
        html = build_mail_html(
            report_date=dates["report_day"],
             is_month_recap=is_month_recap 
        )
    else:
        html = build_mail_html(
            report_date=dates["report_day"],
            image_sources=image_urls,
            is_month_recap=is_month_recap 
        )

    if ENV == "local":
        print("Mode LOCAL → Gmail API")

        SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                "token.json",
                SCOPES
            )

        if not creds or not creds.valid:

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",
                    SCOPES
                )

                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("gmail", "v1", credentials=creds)

        message = MIMEMultipart("mixed")
        related = MIMEMultipart("related")
        message.attach(related)

        message["Subject"] = "Reporting Quotidien ReworldMedia"
        message["From"] = "guillaume@starfox-analytics.com"
        message["To"] = "guillaume@starfox-analytics.com"

        related.attach(MIMEText(html, "html", "utf-8"))

        def attach_image(message, file_path, cid):
            with open(PNG_OUTPUT_DIR + "/" + file_path, "rb") as f:
                img = MIMEImage(f.read())
                img.add_header("Content-ID", f"<{cid}>")
                message.attach(img)

        attach_image(related, "daily_kpi_web.png", "daily_web")
        attach_image(related, "daily_performance_indicators.png", "daily_performance")
        attach_image(related, "daily_top_subscriptions.png", "daily_top_subscriptions")

        attach_image(related, "mtd_kpi_web.png", "mtd_web")
        attach_image(related, "mtd_performance_indicators.png", "mtd_performance")
        attach_image(related, "mtd_top_subscriptions.png", "mtd_top_subscriptions")

        attach_image(related, "ytd_kpi_web.png", "ytd_web")
        attach_image(related, "ytd_performance_indicators.png", "ytd_performance")
        attach_image(related, "ytd_top_subscriptions.png", "ytd_top_subscriptions")

        attach_image(related, "subscription_charts.png", "subscription_charts")

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        print("Email sent (LOCAL Gmail)")

    else:
        print("Mode GCP → n8n")
        send_email_n8n(html)

# -----------------------------
# Setup de l'app
# -----------------------------

app = Flask(__name__)

@app.before_request
def log_request():
    print(f"REQUEST: {request.method} {request.path}")

@app.route("/", methods=["GET"])
def healthcheck():
    return "OK", 200

@app.route("/run", methods=["GET", "POST"])
def run_job():
    try:
        custom_date = request.args.get("date")
        
        if custom_date:
            try:
                datetime.strptime(custom_date, "%d/%m/%Y")
                report_date = custom_date
                print(f"[MANUAL] report_date = {report_date}")
            except ValueError:
                return "Format de date invalide. Utilisez DD/MM/YYYY (ex: 31/05/2026)", 400
        else:
            report_date = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
            print(f"[AUTO] report_date = {report_date}") 

        print("Process started")
        main_process(report_date)
        print("Process finished")
        return f"Job executed successfully for {report_date}", 200

    except Exception:
        print("=== ERREUR PYTHON ===")
        traceback.print_exc()
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    traceback.print_exc()
    return f"<pre>{traceback.format_exc()}</pre>", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
