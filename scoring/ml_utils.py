import os
import joblib
import pandas as pd

# Build absolute paths so it works regardless of where Django is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'ml_models', 'credit_risk_model.pkl')
COLUMNS_PATH = os.path.join(BASE_DIR, 'ml_models', 'model_columns.pkl')

# Load once when Django starts (not on every request)
model = joblib.load(MODEL_PATH)
model_columns = joblib.load(COLUMNS_PATH)


def preprocess_new_customer(raw_data: dict):
    """
    raw_data: dict containing the raw customer data
    Example: {
        'person_age': 25, 'person_income': 50000,
        'person_home_ownership': 'RENT', 'person_emp_length': 3,
        'loan_intent': 'MEDICAL', 'loan_grade': 'B',
        'loan_amnt': 10000, 'loan_int_rate': 11.5,
        'loan_percent_income': 0.2, 'cb_person_default_on_file': 'N',
        'cb_person_cred_hist_length': 4
    }
    """
    df_new = pd.DataFrame([raw_data])

    categorical_cols = ['person_home_ownership', 'loan_intent',
                        'loan_grade', 'cb_person_default_on_file']
    df_encoded = pd.get_dummies(df_new, columns=categorical_cols)

    df_final = df_encoded.reindex(columns=model_columns, fill_value=0)

    bool_cols = df_final.select_dtypes(include='bool').columns
    df_final[bool_cols] = df_final[bool_cols].astype(int)

    return df_final


def get_risk_tier(score: float) -> str:
    if score < 0.3:
        return 'Low'
    elif score < 0.7:
        return 'Medium'
    else:
        return 'High'


def predict_customer(raw_data: dict) -> dict:
    """
    Takes raw customer data and returns risk score + tier.
    This is the single function the Django view will call.
    """
    X_new = preprocess_new_customer(raw_data)
    risk_score = float(model.predict_proba(X_new)[:, 1][0])
    risk_tier = get_risk_tier(risk_score)

    return {
        'risk_score': risk_score,
        'risk_tier': risk_tier
    }