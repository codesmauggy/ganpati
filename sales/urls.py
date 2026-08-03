from rest_framework.routers import DefaultRouter
from .views import RetailBookingViewSet, WholesaleBookingViewSet, TempoViewSet

router = DefaultRouter()
router.register(r'retail-bookings', RetailBookingViewSet, basename='retail-booking')
router.register(r'wholesale-bookings', WholesaleBookingViewSet, basename='wholesale-booking')
router.register(r'tempos', TempoViewSet, basename='tempo')

urlpatterns = router.urls