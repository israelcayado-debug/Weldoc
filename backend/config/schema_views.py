from pathlib import Path

from django.http import HttpResponse
from django.views import View


class StaticSchemaView(View):
    def get(self, request, *args, **kwargs):
        schema_path = Path(__file__).resolve().parents[2] / "openapi.yaml"
        content = schema_path.read_text(encoding="utf-8")
        return HttpResponse(content, content_type="application/yaml")
