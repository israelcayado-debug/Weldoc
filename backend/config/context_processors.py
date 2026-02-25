from django.contrib.auth.models import Group


def _user_groups(user):
    if not user or not user.is_authenticated:
        return set()
    return set(user.groups.values_list("name", flat=True))


def nav_sections(request):
    user = request.user
    groups = _user_groups(user)
    is_admin = bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
    has_assigned_permissions = bool(user and user.is_authenticated and user.get_all_permissions())

    nav = [
        {"label": "Proyectos", "url": "/ui/projects/", "roles": ["Admin", "Project Manager", "PM"]},
        {"label": "Welding Book", "url": "/ui/documents/", "roles": ["Admin", "QA", "Document Control"]},
        {"label": "WPS", "url": "/ui/wps/", "roles": ["Admin", "Welding", "QA"]},
        {"label": "PQR", "url": "/ui/pqr/", "roles": ["Admin", "Welding", "QA"]},
        {"label": "WPQ / Soldadores", "url": "/ui/wpq/", "roles": ["Admin", "Welding", "QA"]},
        {"label": "Welds / Maps", "url": "/ui/welds/maps/", "roles": ["Admin", "Welding", "Production"]},
        {"label": "Calidad (END)", "url": "/ui/quality/nde-requests/", "roles": ["Admin", "QA", "QC"]},
        {"label": "PWHT", "url": "/ui/quality/pwht/", "roles": ["Admin", "QA", "QC"]},
        {"label": "Presion", "url": "/ui/quality/pressure-tests/", "roles": ["Admin", "QA", "QC"]},
        {"label": "Reportes", "url": "/ui/reports/exports/", "roles": ["Admin", "QA", "PM"]},
    ]

    def allowed(item):
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if has_assigned_permissions:
            return True
        if not item["roles"]:
            return True
        return bool(groups.intersection(item["roles"])) or is_admin

    visible = [item for item in nav if allowed(item)]
    return {"nav_sections": visible, "show_admin_nav": is_admin}
