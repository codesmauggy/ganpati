from __future__ import annotations
from django.http import HttpRequest, HttpResponse
from django.urls import re_path
from django.views.generic import TemplateView

API_PREFIXES = ("api/", "static/", "media/", "assets/", "django-admin/")

class SpaFallbackView(TemplateView):
    template_name = "index.html"

    def render_to_response(self, context, **kwargs) -> HttpResponse:
        response = super().render_to_response(context, **kwargs)
        response["Cache-Control"] = "no-cache, must-revalidate"
        return response

def spa_fallback(request: HttpRequest) -> HttpResponse:
    return SpaFallbackView.as_view()(request)

spa_urlpatterns = [
    re_path(r"^(?!(%s)).*$" % "|".join(API_PREFIXES), SpaFallbackView.as_view(), name="spa"),
]