# Customer Risk Score 

Employee-facing tool to look up a customer's credit risk score and view
portfolio-wide risk breakdown.

- **Frontend:** HTML / CSS / JavaScript (Django templates)
- **Backend:** Python (Django)
- **Data:** [Credit Risk Dataset (Kaggle)](https://www.kaggle.com/datasets/laotse/credit-risk-dataset)

## Pages

| Page | URL | Description |
|---|---|---|
| Customer Lookup | `/lookup/` | Search a customer by ID, view their details + risk score |
| Dashboard | `/dashboard/` | Portfolio-wide count of customers per risk tier |

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

Your terminal prompt should now start with `(venv)`. If PowerShell blocks
the activation script with an execution policy error, run this once then
retry:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

This creates your local `db.sqlite3` — every teammate has their own local
copy, it is not shared through git.

```bash
py manage.py migrate
```

### 5. Import the customer data

```bash
py manage.py import_customers credit_risk_clean.csv
```

You should see `Imported 32574 customers.`

## Running the project

```bash
py manage.py runserver
```

Then open:
- http://127.0.0.1:8000/lookup/
- http://127.0.0.1:8000/dashboard/

Stop the server anytime with `Ctrl+C`.
`

## Project structure

```
Customer-risk-score/
├── manage.py
├── requirements.txt
├── credit_risk_clean.csv
├── riskguard_site/          # Django project settings/urls
└── scoring/                 # Main app
    ├── models.py            # Customer model
    ├── views.py             # Lookup + dashboard views
    ├── urls.py
    ├── templates/scoring/   # HTML templates
    └── management/commands/ # import_customers, update_risk_scores
```

## Data columns (Customer model)

| Field | Description |
|---|---|
| `customer_id` | Unique ID, e.g. `CUST_00001` |
| `person_age`, `person_income`, `person_emp_length` | Demographics |
| `person_home_ownership` | RENT / MORTGAGE / OWN |
| `loan_intent`, `loan_grade`, `loan_amnt`, `loan_int_rate` | Loan details |
| `loan_percent_income` | Loan amount as % of income |
| `cb_person_default_on_file` | Prior default on record (Y/N) |
| `cb_person_cred_hist_length` | Credit history length (years) |
| `risk_score` | Model output — probability of default, filled in after ML step |
| `risk_tier` | `High` / `Medium` / `Low`, derived from `risk_score` |

