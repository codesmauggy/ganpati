from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Expense
from .serializers import ExpenseSerializer
from erp.permissions import StaffCanWriteNoDelete

class ExpenseViewSet(ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [StaffCanWriteNoDelete()]

    def perform_create(self, serializer):
        serializer.save(paid_by=self.request.user)