from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Customer, CustomerPayment, LedgerEntry
from .serializers import CustomerSerializer, CustomerPaymentSerializer, CustomerLedgerSerializer
from erp.permissions import IsManager, IsOwnerOrHigher

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrHigher()]
        elif self.action == 'destroy':
            return [IsManager()]
        elif self.action == 'ledger':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager', 'staff']:
            return Customer.objects.all()
        elif user.role in ['wholesaler', 'customer']:
            return Customer.objects.filter(ref_by=user)
        return Customer.objects.none()

    def perform_create(self, serializer):
        serializer.save(ref_by=self.request.user)

    @action(detail=True, methods=['get'])
    def ledger(self, request, pk=None):
        customer = self.get_object()
        if request.user.role in ['wholesaler', 'customer'] and customer.ref_by != request.user:
            return Response({'detail': 'Not allowed.'}, status=403)
        transactions = customer.ledger_entries.order_by('date')
        payments = customer.payments.all()
        bookings = customer.bookings.all()
        data = {
            'customer': customer,
            'transactions': transactions,
            'payments': payments,
            'bookings': bookings,
        }
        serializer = CustomerLedgerSerializer(data)
        return Response(serializer.data)


class PaymentViewSet(ModelViewSet):
    queryset = CustomerPayment.objects.all()
    serializer_class = CustomerPaymentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrHigher()]
        elif self.action == 'destroy':
            return [IsManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager', 'staff']:
            return CustomerPayment.objects.all()
        elif user.role in ['wholesaler', 'customer']:
            return CustomerPayment.objects.filter(customer__ref_by=user)
        return CustomerPayment.objects.none()

    def create(self, request, *args, **kwargs):
        # Debug: print received data
        print("Payment create data:", request.data)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        payment = serializer.save(received_by=self.request.user)
        LedgerEntry.objects.create(
            customer=payment.customer,
            date=payment.date,
            type='Payment',
            reference=payment.payment_id,
            description=f"Payment {payment.mode} - {payment.note or ''}",
            debit=0,
            credit=payment.amount,
            recorded_by=self.request.user
        )