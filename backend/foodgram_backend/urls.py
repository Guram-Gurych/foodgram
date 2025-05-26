import os

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
    path("api/recipes/", include("recipes.urls")),
    path("api/users/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("docs/", TemplateView.as_view(template_name="redoc/index.html")),
        path(
            "static/<path:path>",
            serve,
            {
                "document_root": os.path.join(settings.BASE_DIR, "backend", "static"),
            },
        ),
    ]
