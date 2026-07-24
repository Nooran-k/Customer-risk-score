from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from .models import Customer

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