from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Booking, Tempo
from .serializers import BookingSerializer, TempoSerializer
from erp.permissions import IsManager, IsOwnerOrHigher, StaffCanWriteNoDelete

class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all().order_by('-date')
    serializer_class = BookingSerializer

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
            return Booking.objects.all()
        elif user.role in ['wholesaler', 'customer']:
            return Booking.objects.filter(collector=user) | Booking.objects.filter(customer__ref_by=user)
        return Booking.objects.none()

    def perform_create(self, serializer):
        # The serializer will set collector from context
        serializer.save()

class TempoViewSet(ModelViewSet):
    queryset = Tempo.objects.all()
    serializer_class = TempoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [StaffCanWriteNoDelete()]