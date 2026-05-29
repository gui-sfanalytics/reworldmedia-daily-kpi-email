# 📊 Daily KPI Reporting – BigQuery → Email

## 🚀 Overview

Cette application permet de :

- Extraire des données depuis Google BigQuery
- Calculer des KPI (daily, MTD, YTD)
- Générer des visuels (HTML → PNG)
- Envoyer un email avec les résultats

---

## ⚙️ Modes

### LOCAL
- Génération HTML + PNG en local
- Envoi via Gmail API
- Pas de GCS / webhook

### PROD
- Upload GCS
- Envoi via webhook (n8n)
- Pas de Gmail API

---

## 🔧 Configuration

Variable d'environnement :

ENV=local ou ENV=prod

---

## ▶️ Lancer en local

### Windows (PowerShell)

$env:ENV="local"
python main.py

Puis ouvrir :
http://127.0.0.1:8080

---

## ☁️ Déploiement Cloud Run

gcloud run deploy reworldmedia-daily-mail-kpi --source . --region europe-west1

---

## 📁 Structure

- main.py
- src/
- templates/
- queries/

---

## 📊 Sources BigQuery

- import_data.sylius_imports
- import_data.target_forecast_produits
- reporting.referentiel_titres

---

## 🖼️ Génération

HTML → PNG via Playwright

---

## 📧 Envoi

LOCAL : Gmail API  
PROD : webhook n8n

---

## 🧪 Debug

Ajouter :

print(f"ENV = {ENV}")

---

## ✅ Tips

- Vérifier playwright install
- Vérifier credentials Gmail
- Vérifier upload GCS en prod

---

## 🚀 Stack

Python, BigQuery, Flask, Playwright, GCP
