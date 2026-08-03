from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from catalog.models import Category   # now exists
from .models import CompanySettings

User = get_user_model()

class SettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company, _ = CompanySettings.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Manish Kala Kendra',
                'since': '1989',
                'address': 'Karjat, Maharashtra',
                'gst': '27ABCDE1234F1Z5',
            }
        )

        # Collectors – users with roles admin/manager/staff
        collectors = User.objects.filter(role__in=['admin', 'manager', 'staff'])
        collectors_data = [
            {
                'name': u.get_full_name() or u.username,
                'role': u.get_role_display() if hasattr(u, 'get_role_display') else u.role
            }
            for u in collectors
        ]

        categories = Category.objects.all()
        categories_data = [
            {'name': c.name, 'type': getattr(c, 'type', 'Primary')}
            for c in categories
        ]

        payment_modes = [
            {'name': 'Cash', 'enabled': True},
            {'name': 'UPI', 'enabled': True},
            {'name': 'Bank Transfer', 'enabled': True},
            {'name': 'Cheque', 'enabled': True},
        ]

        data = {
            'company': {
                'name': company.name,
                'since': company.since,
                'address': company.address,
                'gst': company.gst,
            },
            'collectors': collectors_data,
            'categories': categories_data,
            'paymentModes': payment_modes,
        }
        return Response(data)