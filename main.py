import os

from jinja2 import Environment, FileSystemLoader
from matplotlib import dates
from playwright.sync_api import sync_playwright
from google.cloud import bigquery, storage
from flask import Flask

import base64
import requests

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.data import calcul_data, calcul_data_product
from templates.full_mail import build_mail_html
from src.charts import create_subscription_charts

from datetime import datetime, timedelta

ENV = os.getenv("ENV", "local") 
HTML_OUTPUT_DIR = "src/outputs/html"
PNG_OUTPUT_DIR = "src/outputs/png"
SQL_DIR = "src/queries"
os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)
os.makedirs(PNG_OUTPUT_DIR, exist_ok=True)
os.makedirs(SQL_DIR, exist_ok=True)


#variable globale
#report_date =  "26/05/2026";
report_date = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")

# -----------------------------
# manipulation dates
# -----------------------------


def get_same_weekday_last_year(date_obj):
    iso_year, iso_week, iso_weekday = date_obj.isocalendar()
    target_year = iso_year - 1
    first_day = datetime.strptime(f"{target_year}-W{iso_week:02d}-1", "%G-W%V-%u")
    return first_day + timedelta(days=iso_weekday - 1)

def main_process():

    print("Process started")

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
            browser = p.chromium.launch()

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

    def upload_to_gcs(local_path, bucket_name, destination_blob_name):
        if ENV == "local":
            print(f"[LOCAL] Skip upload {local_path}")
            return None

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(local_path)

        #url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"

        #url signés
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET"
        )

        print(f"Uploaded {local_path} to {url}")

        return url

    client = bigquery.Client()

    env = Environment(
        loader=FileSystemLoader("templates")
    )

    # -----------------------------
    # Appel des queries
    # -----------------------------


    def generate_period_report(period_name, query_file, product_query_file, report_title, current_date, previous_date):
        
        report_date_minus2 = (datetime.strptime(report_date, "%d/%m/%Y") - timedelta(days=2)).strftime("%Y-%m-%d")


        with open(SQL_DIR + "/" + query_file, "r", encoding="utf-8") as f:
            query = f.read().format(report_date=dates['report_day_sql'], report_date_minus2=report_date_minus2)

        query_job = client.query(query)
        rows = list(query_job.result())

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
            kpi["delta_display"] = f"{kpi['delta_percent']:+.0f}%"

            max_value = max(kpi["current_value"], kpi["target_value"]) * 1.08 if max(kpi["current_value"], kpi["target_value"]) else 1
            kpi["current_percent_clamped"] = min(100, max(0, round(kpi["current_value"] / max_value * 100, 1)))
            kpi["target_percent_clamped"] = min(100, max(0, round(kpi["target_value"] / max_value * 100, 1)))

        with open( SQL_DIR + "/" + product_query_file, "r", encoding="utf-8") as f:
            query = f.read().format(report_date=dates['report_day_sql'], report_date_minus2=report_date_minus2)

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
            "kpi-email-storage",  # nom du bucket
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
            "kpi-email-storage",  # nom du bucket
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
            "kpi-email-storage",  # nom du bucket
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
            "months": months,  # pour graph 1
            "sliding_year": abo_m,
            "sliding_year_n1": abo_m_n1,
            "objectifs": target_month,

            # graph 2 filtré
            "consolidated": abo_ytd_filtered,
            "consolidated_n1": abo_ytd_n1_filtered,
            "consolidated_obj": target_ytd_filtered,

            # months aussi filtré pour graph 2
            "months_ytd": months_ytd,
    }

    dates = compute_dates(report_date)
    image_urls = {}

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

    def send_email_n8n(html, image_urls):
        url = "https://app.starfox-analytics.com/webhook/gmail-send-html"

        # inject images dynamiques
        for key, value in image_urls.items():
            if value:
                html += f'<br><img src="{value}" width="700">'

        to_list, cc_list, bcc_list = get_recipients()

        payload = {
            "to": to_list,
            "cc": cc_list,
            "bcc": bcc_list,
            "subject": "Daily KPI Report",
            "html": html
        }

        response = requests.post(url, json=payload)

        print("n8n:", response.status_code, response.text)

        if response.status_code >= 300:
            raise Exception("Email failed via n8n")

    html = build_mail_html(
        report_date=dates["report_day"]
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

        message["Subject"] = "Daily KPI Report"
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

        send_email_n8n(html, image_urls)


    # -----------------------------
    # Setup de l'app
    # -----------------------------

app = Flask(__name__)

@app.route("/")
def run():
    try:
        main_process()
        return "OK", 200
    except Exception as e:
        print(str(e))
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)