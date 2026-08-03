from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import RetailBooking, WholesaleBooking, Tempo
from .serializers import RetailBookingSerializer, WholesaleBookingSerializer, TempoSerializer
from erp.permissions import IsManager, IsOwnerOrHigher, StaffCanWriteNoDelete


class RetailBookingViewSet(ModelViewSet):
    queryset = RetailBooking.objects.all().order_by('-date')
    serializer_class = RetailBookingSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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
            return RetailBooking.objects.all()
        elif user.role in ['wholesaler', 'customer']:
            return RetailBooking.objects.filter(collector=user) | RetailBooking.objects.filter(customer__ref_by=user)
        return RetailBooking.objects.none()


class WholesaleBookingViewSet(ModelViewSet):
    queryset = WholesaleBooking.objects.all().order_by('-date')
    serializer_class = WholesaleBookingSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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
            return WholesaleBooking.objects.all()
        elif user.role in ['wholesaler', 'customer']:
            return WholesaleBooking.objects.filter(collector=user) | WholesaleBooking.objects.filter(customer__ref_by=user)
        return WholesaleBooking.objects.none()


class TempoViewSet(ModelViewSet):
    queryset = Tempo.objects.all()
    serializer_class = TempoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [StaffCanWriteNoDelete()]