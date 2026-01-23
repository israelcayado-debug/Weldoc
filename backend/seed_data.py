import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from apps.users import models as user_models
from apps.projects import models as project_models
from apps.wps import models as wps_models


def run():
    roles = ["Admin", "Supervisor", "Inspector", "Soldador"]
    for name in roles:
        user_models.Role.objects.get_or_create(name=name, defaults={"scope": "global"})

    admin_email = "admin@example.local"
    app_user, _ = user_models.User.objects.get_or_create(
        email=admin_email, defaults={"name": "admin", "status": "active"}
    )
    admin_role = user_models.Role.objects.get(name="Admin")
    user_models.UserRole.objects.get_or_create(user=app_user, role=admin_role)

    project, _ = project_models.Project.objects.get_or_create(
        code="P1",
        defaults={
            "name": "Proyecto Demo",
            "units": "metric",
            "status": "active",
            "standard_set": ["ASME_IX"],
        },
    )
    project_models.ProjectUser.objects.get_or_create(
        project=project, user=app_user, role=admin_role
    )

    wps_models.MaterialBase.objects.get_or_create(spec="ASTM A36")
    wps_models.FillerMaterial.objects.get_or_create(spec="ER70S-6")
    wps_models.JointType.objects.get_or_create(code="BW")


if __name__ == "__main__":
    run()
