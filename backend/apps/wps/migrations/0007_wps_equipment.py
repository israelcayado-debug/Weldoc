import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_project_equipment_rename"),
        ("wps", "0006_pqr_scanned_pdf"),
    ]

    operations = [
        migrations.AddField(
            model_name="wps",
            name="equipment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="projects.projectequipment",
            ),
        ),
    ]
