from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .spa import spa_urlpatterns
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet  

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')  # 👈 register here

urlpatterns = [
    path('admin/', RedirectView.as_view(url='/django-admin/', permanent=True)),
    path('django-admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('catalog.urls')),
    path('api/', include('sales.urls')),
    path('api/', include('workforce.urls')),
    path('api/', include('expenses.urls')),
    path('api/', include('customers.urls')),
    path('api/', include('reports.urls')),
    path('api/', include(router.urls)),
    *spa_urlpatterns,   # catch-all fallback – keep LAST
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)