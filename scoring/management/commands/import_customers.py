import pandas as pd
from django.core.management.base import BaseCommand
from scoring.models import Customer

class Command(BaseCommand):
    help = "Import cleaned customer data from Nour's CSV"

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)

    def handle(self, *args, **options):
        df = pd.read_csv(options['csv_path'])
        created_count = 0

        for _, row in df.iterrows():
            Customer.objects.update_or_create(
                customer_id=row['customer_id'],
                defaults={
                    'person_age': row['person_age'],
                    'person_income': row['person_income'],
                    'person_emp_length': row.get('person_emp_length'),
                    'person_home_ownership': row['person_home_ownership'],
                    'loan_intent': row['loan_intent'],
                    'loan_grade': row['loan_grade'],
                    'loan_amnt': row['loan_amnt'],
                    'loan_int_rate': row.get('loan_int_rate'),
                    'loan_percent_income': row['loan_percent_income'],
                    'cb_person_default_on_file': row['cb_person_default_on_file'],
                    'cb_person_cred_hist_length': row['cb_person_cred_hist_length'],
                }
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {created_count} customers."))