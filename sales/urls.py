from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, TempoViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'tempos', TempoViewSet, basename='tempo')
urlpatterns = router.urls