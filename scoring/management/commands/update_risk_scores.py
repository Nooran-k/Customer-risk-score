import pandas as pd
from django.core.management.base import BaseCommand
from scoring.models import Customer

class Command(BaseCommand):
    help = "Update risk_score and risk_tier from Hussien's model output"

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)

    def handle(self, *args, **options):
        df = pd.read_csv(options['csv_path'])
        updated_count = 0
        missing_count = 0

        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['customer_id'])
                customer.risk_score = row['risk_score']
                customer.risk_tier = row['risk_tier']
                customer.save()
                updated_count += 1
            except Customer.DoesNotExist:
                missing_count += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} customers."))
        if missing_count:
            self.stdout.write(self.style.WARNING(f"{missing_count} customer_ids were not found."))