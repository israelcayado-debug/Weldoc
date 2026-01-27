from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularSwaggerView
from config.schema_views import StaticSchemaView
from config.views import home


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("config.api_urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("", include("apps.welds.urls")),
    path("ui/wps/", include("apps.wps.ui_urls")),
    path("ui/wpq/", include("apps.wpq.ui_urls")),
    path("ui/projects/", include("apps.projects.ui_urls")),
    path("ui/documents/", include("apps.documents.ui_urls")),
    path("ui/welds/", include("apps.welds.ui_urls")),
    path("ui/reports/", include("apps.reports.ui_urls")),
    path("ui/quality/", include("apps.quality.ui_urls")),
    path("api/schema/", StaticSchemaView.as_view(), name="static-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="static-schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
