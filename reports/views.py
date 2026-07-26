from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from catalog.models import Model
from sales.models import Booking
from expenses.models import Expense
from workforce.models import Worker
from customers.models import CustomerPayment

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_stock = Model.objects.aggregate(total=Sum('available'))['total'] or 0
        total_models = Model.objects.count()
        wholesale_value = Booking.objects.filter(channel='Wholesale').aggregate(total=Sum('amount'))['total'] or 0
        retail_value = Booking.objects.filter(channel='Retail').aggregate(total=Sum('amount'))['total'] or 0
        wholesale_count = Booking.objects.filter(channel='Wholesale').count()
        retail_count = Booking.objects.filter(channel='Retail').count()
        collection = CustomerPayment.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_billed = Booking.objects.aggregate(total=Sum('amount'))['total'] or 0
        pending = total_billed - collection
        expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        staff_payments = Worker.objects.aggregate(total=Sum('pending_salary'))['total'] or 0
        net_profit = collection - expenses - staff_payments
        low_stock_count = Model.objects.filter(available__lte=F('low_stock_at')).count()

        data = {
            'total_stock': total_stock,
            'total_models': total_models,
            'wholesale_value': wholesale_value,
            'retail_value': retail_value,
            'wholesale_count': wholesale_count,
            'retail_count': retail_count,
            'collection': collection,
            'pending': pending,
            'expenses': expenses,
            'staff_payments': staff_payments,
            'net_profit': net_profit,
            'low_stock_count': low_stock_count,
        }
        return Response(data)