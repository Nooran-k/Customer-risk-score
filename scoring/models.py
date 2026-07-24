from django.db import models

class Customer(models.Model):
    customer_id = models.CharField(max_length=20, primary_key=True)
    person_age = models.IntegerField()
    person_income = models.FloatField()
    person_emp_length = models.FloatField(null=True)
    person_home_ownership = models.CharField(max_length=20)
    loan_intent = models.CharField(max_length=30)
    loan_grade = models.CharField(max_length=5)
    loan_amnt = models.FloatField()
    loan_int_rate = models.FloatField(null=True)
    loan_percent_income = models.FloatField()
    cb_person_default_on_file = models.CharField(max_length=5)
    cb_person_cred_hist_length = models.IntegerField()

    # Placeholder until Hussien's model output arrives
    risk_score = models.FloatField(null=True, blank=True, default=None)
    risk_tier = models.CharField(max_length=10, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.customer_id} ({self.risk_tier or 'unscored'})"