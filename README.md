# RiskLens — Customer Credit Risk Scoring System

An ML-powered credit risk scoring engine and internal web application for
Banque Misr, built as a Data Science internship project. Given a customer's
financial and loan details, the system predicts their probability of default
and classifies them into a Low / Medium / High risk tier — helping bank
employees make faster, more consistent lending decisions.

## Live Demo Features

- **Customer Lookup** — search any existing customer by ID and view their
  full profile, risk score, and tier
- **Dashboard** — live, portfolio-wide breakdown of risk tiers, loan grade
  distribution, home ownership, average loan-to-income and interest rate by
  tier, and risk trend by age group
- **Add New Customer** — enter a brand-new applicant's details and get an
  instant risk score, generated live by the trained model
- **Bulk Upload** — upload an Excel file of multiple new applicants and score
  them all at once
- **PDF Reports** — download any customer's risk profile as a formatted PDF

## Project Pipeline

```
Raw Data → Cleaning → EDA → Feature Engineering →
Model Training (SMOTE + LightGBM) → Risk Scoring →
Django Web Application (Lookup, Dashboard, Live Prediction)
```

## Tech Stack

| Layer | Tools |
|---|---|
| Data & Analysis | Python, Pandas, NumPy |
| Visualization | Matplotlib, Seaborn, Chart.js |
| Machine Learning | scikit-learn, LightGBM, imbalanced-learn (SMOTE), SHAP |
| Backend | Django |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| PDF Generation | ReportLab |

## Dataset

[Credit Risk Dataset (Kaggle)](https://www.kaggle.com/datasets/laotse/credit-risk-dataset)
— 32,574 customers after cleaning, 12 raw features (demographics, loan
details, credit bureau history), target: `loan_status` (defaulted / repaid).
(note: no real bank misr customer data was used in this project )

## Model

- **Algorithm:** LightGBM, benchmarked against 7 other classical ML models
  (Logistic Regression, Decision Tree, Random Forest, Gradient Boosting,
  XGBoost, KNN, Naive Bayes)
- **Class imbalance:** handled with SMOTE (applied to training data only)
- **Performance:** 0.945 test AUC, 93% accuracy, 0.97 precision / 0.83 recall
  on defaulters
- **Threshold:** decision cutoff tuned from 0.50 → 0.30 to prioritize
  catching real defaulters over avoiding false alarms
- **Explainability:** SHAP values used to identify which features drive each
  prediction

### Risk Tiers

| Tier | Risk Score |
|---|---|
| Low | < 0.30 |
| Medium | 0.30 – 0.70 |
| High | ≥ 0.70 |

## Setup — first time only

### 1. Clone the repo

```bash
git clone <repo-url>
cd Customer-risk-score
```

### 2. Create a virtual environment

**Windows (PowerShell):**
```powershell
py -m venv venv
venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

If PowerShell blocks the activation script:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

```bash
py manage.py migrate
```

### 5. Import the cleaned customer data

```bash
py manage.py import_customers preprocessing/credit_risk_clean.csv
```

### 6. Load the model's risk scores

```bash
py manage.py update_risk_scores Model/credit_risk_scored.csv
```

## Running the project

```bash
py manage.py runserver
```

Then open:
- `http://127.0.0.1:8000/lookup/` — Customer Lookup
- `http://127.0.0.1:8000/dashboard/` — Dashboard
- `http://127.0.0.1:8000/add-customer/` — Add New Customer
- `http://127.0.0.1:8000/predict-excel/` — Bulk Upload

These URLs only work while the server is running on your own machine ! you need to run the
setup steps above and start your own local server.

## Project Structure

```
Customer-risk-score/
├── manage.py
├── requirements.txt
├── 01_EDA
├── preprocessing/            # Data cleaning notebooks + cleaned CSVs
├── Model/                    # Model training notebooks + scored CSV
├── riskguard_site/           # Django project settings/urls
└── scoring/                  # Main app
    ├── models.py             # Customer model
    ├── views.py               # All page + API logic
    ├── urls.py
    ├── ml_utils.py            # Live model loading + prediction function
    ├── ml_models/             # Trained model + column reference (.pkl)
    ├── templates/scoring/     # HTML templates
    └── management/commands/  # import_customers, update_risk_scores
```

## Data Columns (Customer model)

| Field | Description |
|---|---|
| `customer_id` | Unique ID, e.g. `CUST_00001` |
| `person_age`, `person_income`, `person_emp_length` | Demographics |
| `person_home_ownership` | RENT / MORTGAGE / OWN / OTHER |
| `loan_intent`, `loan_grade`, `loan_amnt`, `loan_int_rate` | Loan details |
| `loan_percent_income` | Loan amount as % of income |
| `cb_person_default_on_file` | Prior default on record (Y/N) |
| `cb_person_cred_hist_length` | Credit history length (years) |
| `risk_score` | Model's predicted probability of default |
| `risk_tier` | `Low` / `Medium` / `High`, derived from `risk_score` |

