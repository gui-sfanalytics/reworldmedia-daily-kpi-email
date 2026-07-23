# 📊 Daily KPI Reporting – BigQuery → Email

## 🚀 Overview

Cette application permet de :

- Extraire des données depuis Google BigQuery
- Calculer des KPI (daily, MTD, YTD) par performance globale et par produit/titre
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

```
ENV=local ou ENV=prod
```

---

## ▶️ Lancer en local

### Windows (PowerShell)

```powershell
$env:ENV="local"
python main.py
```

Puis ouvrir :
http://127.0.0.1:8080

Pour envoyer un mail en local à la date d'aujourd'hui
http://127.0.0.1:8080/run

Pour envoer un mail en local à une date donnée
http://127.0.0.1:8080/run?date=18/07/2026

---

## ☁️ Déploiement Cloud Run

```bash
gcloud run deploy reworldmedia-daily-mail-kpi --source . --region europe-west1
```

---

## 📁 Structure

```
├── main.py
├── src/
├── templates/
├── queries/
```

---

## 📊 Sources BigQuery

### Tables sources (raw)

| Table | Description |
|---|---|
| `import_data.sylius_imports` | Commandes / abonnements |
| `import_data.target_forecast_produits` | Objectifs par produit |
| `reporting.referentiel_titres` | Référentiel des titres/magazines |
| `reporting.calendrier` | Calendrier avec correspondances N-1 |

### Tables de reporting (calculées)

| Table | Procédure | Description |
|---|---|---|
| `reporting.perf_mail_daily` | `load_mail_perf_daily` | KPI globaux quotidiens (abonnements, marketplace, réabonnements, numéros) |
| `reporting.product_mail_daily` | `load_mail_product_daily` | KPI quotidiens par titre/produit (abonnements papier) |
| `reporting.ga4_mail_daily` | `load_mail_ga4_daily` | KPI sessions GA4 quotidiens |

---

## 🔄 Pipeline BigQuery

### Procédures stockées

Chaque table de reporting est alimentée par une procédure BigQuery schedulée quotidiennement.

#### Fonctionnement quotidien (mode production)

```sql
DECLARE v_start_date DATE DEFAULT DATE_SUB(CURRENT_DATE("Europe/Paris"), INTERVAL 1 DAY);
DECLARE v_end_date   DATE DEFAULT DATE_SUB(CURRENT_DATE("Europe/Paris"), INTERVAL 1 DAY);
```

#### Recalcul manuel (correctif ou recalcul historique)

```sql
DECLARE v_start_date DATE DEFAULT DATE '2026-01-01';
DECLARE v_end_date   DATE DEFAULT DATE '2026-06-01';
```

> 💡 Recommandé : relancer sur `DATE_TRUNC(MONTH)` → hier une fois par semaine pour corriger d'éventuelles annulations rétroactives dans Sylius.

### Architecture des CTEs

Les procédures utilisent une séparation en deux CTEs pour garantir la cohérence des KPIs cumulatifs (MTD, YTD) :

| CTE | Filtre | Rôle |
|---|---|---|
| `product_history` / `order_history` | `01/01/N-1` → `v_end_date` | Historique complet pour les calculs N-1, MTD, YTD |
| `product_current` / `daily_current` | `v_start_date` → `v_end_date` | Uniquement les jours à insérer/mettre à jour |

> ⚠️ Sans cette séparation, `abo_a1` (YTD) pouvait être inférieur au jour précédent lors d'un run quotidien.

### Stratégie MERGE

- `WHEN MATCHED → UPDATE` : écrase les valeurs existantes (idempotent)
- `WHEN NOT MATCHED → INSERT` : insère les nouvelles lignes
- `DELETE` préalable sur la plage `v_start_date → v_end_date` avant chaque MERGE

### Pipeline logs

Chaque exécution est tracée dans `import_data.pipeline_logs` :

| Champ | Description |
|---|---|
| `status` | `SUCCESS` ou `ERROR` |
| `rows_inserted` | Nombre de lignes traitées |
| `error_message` | Message d'erreur si applicable |
| `started_at` / `ended_at` | Timestamps d'exécution |

---

## 📈 KPIs calculés

### perf_mail_daily & product_mail_daily

| KPI | Description |
|---|---|
| `abo_j` | Abonnements du jour J |
| `abo_j_n1` | Abonnements même jour de semaine N-1 |
| `evol_abo_j_n1` | Évolution % J vs N-1 |
| `abo_m1` | Abonnements cumulés MTD (Month-To-Date) |
| `abo_m1_n1` | MTD N-1 à date équivalente |
| `evol_abo_m1_n1` | Évolution % MTD vs N-1 |
| `abo_a1` | Abonnements cumulés YTD (Year-To-Date) |
| `abo_a1_n1` | YTD N-1 à date équivalente |
| `evol_abo_a1_n1` | Évolution % YTD vs N-1 |
| `target_abo_j/m1/a1` | Objectifs jour / MTD / YTD |

---

## 🖼️ Génération

HTML → PNG via **Playwright**

---

## 📧 Envoi

| Mode | Méthode |
|---|---|
| `LOCAL` | Gmail API |
| `PROD` | Webhook n8n |

---

## 🧪 Debug

```python
print(f"ENV = {ENV}")
```

Vérifications courantes :
- ✅ `playwright install` exécuté
- ✅ Credentials Gmail configurés
- ✅ Upload GCS fonctionnel en PROD
- ✅ Procédures BigQuery schedulées et actives
- ✅ `pipeline_logs` sans erreurs récentes

---

## 🔁 Maintenance

### Recalcul complet recommandé (1x/semaine)

```sql
CALL `sfx-reworld-media.import_data.load_mail_perf_daily`();
-- avec v_start_date = DATE_TRUNC(CURRENT_DATE, MONTH)
--      v_end_date   = DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY)
```

Répéter pour `load_mail_product_daily` et `load_mail_ga4_daily`.

---

## 🚀 Stack

| Technologie | Usage |
|---|---|
| Python | Application principale |
| Google BigQuery | Stockage et calcul des KPIs |
| Flask | Serveur local de preview |
| Playwright | Génération HTML → PNG |
| Google Cloud Run | Déploiement PROD |
| Google Cloud Storage | Stockage images PROD |
| n8n | Orchestration envoi email PROD |
| Gmail API | Envoi email LOCAL |
