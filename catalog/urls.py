from rest_framework.routers import DefaultRouter
from .views import ModelViewSet

router = DefaultRouter()
router.register(r'models', ModelViewSet, basename='model')
urlpatterns = router.urls