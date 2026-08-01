from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from .models import Customer
from django.db.models import Avg, Count, Case, When, Value, CharField
import pandas as pd
from .ml_utils import predict_customer
import uuid
#for pdf generation ↓
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def customer_lookup(request):
    customer = None
    error = None

    if request.method == 'POST':
        customer_id = request.POST.get('customer_id', '').strip()
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            error = f"No customer found with ID '{customer_id}'."

    return render(request, 'scoring/lookup.html', {
        'customer': customer,
        'error': error,
    })

def dashboard(request):
    return render(request, 'scoring/dashboard.html')

def tier_counts_api(request):
    counts = Customer.objects.values('risk_tier').annotate(count=Count('customer_id'))
    data = {row['risk_tier'] or 'Unscored': row['count'] for row in counts}
    return JsonResponse(data)

def tier_averages_api(request):
    data = (
        Customer.objects
        .exclude(risk_tier__isnull=True)
        .values('risk_tier')
        .annotate(
            avg_loan_pct_income=Avg('loan_percent_income'),
            avg_int_rate=Avg('loan_int_rate'),
        )
    )
    result = {
        row['risk_tier']: {
            'avg_loan_pct_income': round(row['avg_loan_pct_income'] or 0, 3),
            'avg_int_rate': round(row['avg_int_rate'] or 0, 2),
        }
        for row in data
    }
    return JsonResponse(result)


def loan_grade_by_tier_api(request):
    data = (
        Customer.objects
        .exclude(risk_tier__isnull=True)
        .values('risk_tier', 'loan_grade')
        .annotate(count=Count('customer_id'))
    )
    result = {}
    for row in data:
        tier = row['risk_tier']
        result.setdefault(tier, {})
        result[tier][row['loan_grade']] = row['count']
    return JsonResponse(result)


def home_ownership_api(request):
    data = (
        Customer.objects
        .values('person_home_ownership')
        .annotate(count=Count('customer_id'))
    )
    result = {row['person_home_ownership']: row['count'] for row in data}
    return JsonResponse(result)


def high_risk_loan_intent_api(request):
    data = (
        Customer.objects
        .filter(risk_tier='High')
        .values('loan_intent')
        .annotate(count=Count('customer_id'))
    )
    result = {row['loan_intent']: row['count'] for row in data}
    return JsonResponse(result)


def risk_by_age_group_api(request):
    data = (
        Customer.objects
        .exclude(risk_score__isnull=True)
        .annotate(
            age_group=Case(
                When(person_age__lt=25, then=Value('20-24')),
                When(person_age__lt=30, then=Value('25-29')),
                When(person_age__lt=35, then=Value('30-34')),
                When(person_age__lt=40, then=Value('35-39')),
                When(person_age__lt=45, then=Value('40-44')),
                When(person_age__lt=50, then=Value('45-49')),
                When(person_age__lt=60, then=Value('50-59')),
                default=Value('60+'),
                output_field=CharField(),
            )
        )
        .values('age_group')
        .annotate(avg_risk=Avg('risk_score'))
        .order_by('age_group')
    )
    result = {row['age_group']: round(row['avg_risk'] or 0, 3) for row in data}
    return JsonResponse(result)



def add_customer(request):
    result = None
    error = None

    if request.method == 'POST':
        try:
            raw_data = {
                'person_age': int(request.POST['person_age']),
                'person_income': float(request.POST['person_income']),
                'person_home_ownership': request.POST['person_home_ownership'],
                'person_emp_length': float(request.POST['person_emp_length']),
                'loan_intent': request.POST['loan_intent'],
                'loan_grade': request.POST['loan_grade'],
                'loan_amnt': float(request.POST['loan_amnt']),
                'loan_int_rate': float(request.POST['loan_int_rate']),
                'loan_percent_income': float(request.POST['loan_percent_income']),
                'cb_person_default_on_file': request.POST['cb_person_default_on_file'],
                'cb_person_cred_hist_length': int(request.POST['cb_person_cred_hist_length']),
            }

            prediction = predict_customer(raw_data)

            new_id = f"CUST_{uuid.uuid4().hex[:8].upper()}"
            customer = Customer.objects.create(
                customer_id=new_id,
                **raw_data,
                risk_score=prediction['risk_score'],
                risk_tier=prediction['risk_tier'],
            )
            result = customer

        except Exception as e:
            error = f"Something went wrong: {e}"

    return render(request, 'scoring/add_customer.html', {
        'result': result,
        'error': error,
    })

def predict_from_excel(request):
    results = []
    errors = []

    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')

        if not excel_file:
            errors.append("No file was uploaded.")
        else:
            try:
                df_upload = pd.read_excel(excel_file)
            except Exception as e:
                errors.append(f"Couldn't read the file: {e}")
                df_upload = None

            if df_upload is not None:
                required_cols = [
                    'person_age', 'person_income', 'person_home_ownership',
                    'person_emp_length', 'loan_intent', 'loan_grade',
                    'loan_amnt', 'loan_int_rate', 'loan_percent_income',
                    'cb_person_default_on_file', 'cb_person_cred_hist_length',
                ]
                missing_cols = [c for c in required_cols if c not in df_upload.columns]

                if missing_cols:
                    errors.append(f"Missing required columns: {', '.join(missing_cols)}")
                else:
                    for i, row in df_upload.iterrows():
                        try:
                            raw_data = {
                                'person_age': int(row['person_age']),
                                'person_income': float(row['person_income']),
                                'person_home_ownership': str(row['person_home_ownership']),
                                'person_emp_length': float(row['person_emp_length']),
                                'loan_intent': str(row['loan_intent']),
                                'loan_grade': str(row['loan_grade']),
                                'loan_amnt': float(row['loan_amnt']),
                                'loan_int_rate': float(row['loan_int_rate']),
                                'loan_percent_income': float(row['loan_percent_income']),
                                'cb_person_default_on_file': str(row['cb_person_default_on_file']),
                                'cb_person_cred_hist_length': int(row['cb_person_cred_hist_length']),
                            }

                            prediction = predict_customer(raw_data)
                            new_id = f"CUST_{uuid.uuid4().hex[:8].upper()}"

                            customer = Customer.objects.create(
                                customer_id=new_id,
                                **raw_data,
                                risk_score=prediction['risk_score'],
                                risk_tier=prediction['risk_tier'],
                            )
                            results.append(customer)

                        except Exception as e:
                            errors.append(f"Row {i + 2}: {e}")  # +2 = header row + 0-index

    return render(request, 'scoring/bulk_upload.html', {
        'results': results,
        'errors': errors,
    })

def customer_pdf(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return HttpResponse("Customer not found.", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{customer.customer_id}_risk_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=0.6*inch, bottomMargin=0.6*inch)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], textColor=colors.HexColor('#A6192E'))
    elements.append(Paragraph("Banque Misr - Customer Risk Report", title_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"Customer ID: {customer.customer_id}", styles['Heading2']))
    elements.append(Spacer(1, 12))

    tier_colors = {
        'High': colors.HexColor('#D92D3F'),
        'Medium': colors.HexColor('#DDA524'),
        'Low': colors.HexColor('#1F9D55'),
    }
    tier_color = tier_colors.get(customer.risk_tier, colors.grey)

    risk_table = Table([
        ['Risk Tier', customer.risk_tier or 'Not yet scored'],
        ['Risk Score', f"{customer.risk_score:.4f}" if customer.risk_score is not None else 'N/A'],
    ], colWidths=[2*inch, 4*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FAF9F7')),
        ('TEXTCOLOR', (1, 0), (1, 0), tier_color),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ECE6DC')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Applicant Details", styles['Heading2']))
    elements.append(Spacer(1, 8))

    details = [
        ['Age', str(customer.person_age)],
        ['Income', f"${customer.person_income:,.2f}"],
        ['Employment Length', f"{customer.person_emp_length} yrs"],
        ['Home Ownership', customer.person_home_ownership],
        ['Loan Intent', customer.loan_intent],
        ['Loan Grade', customer.loan_grade],
        ['Loan Amount', f"${customer.loan_amnt:,.2f}"],
        ['Interest Rate', f"{customer.loan_int_rate}%"],
        ['Loan % of Income', str(customer.loan_percent_income)],
        ['Prior Default on File', customer.cb_person_default_on_file],
        ['Credit History Length', f"{customer.cb_person_cred_hist_length} yrs"],
    ]
    details_table = Table(details, colWidths=[2.2*inch, 3.8*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FAF9F7')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ECE6DC')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 24))

    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], textColor=colors.HexColor('#6B6258'), fontSize=8)
    elements.append(Paragraph("Generated by RiskLens - Banque Misr Internal Risk Scoring System", footer_style))

    doc.build(elements)
    return response