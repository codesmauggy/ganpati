from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'payments', PaymentViewSet, basename='payment')
urlpatterns = router.urls