from django.db import migrations, models


def resequence_revisions(apps, schema_editor):
    Wps = apps.get_model("wps", "Wps")
    rows = list(
        Wps.objects.all()
        .order_by("project_id", "code", "revision_number", "id")
        .values("id", "project_id", "code", "revision_number")
    )
    current_key = None
    next_rev = 0
    for row in rows:
        key = (row["project_id"], row["code"])
        if key != current_key:
            current_key = key
            next_rev = 0
        Wps.objects.filter(id=row["id"]).update(revision_number=next_rev)
        next_rev += 1


class Migration(migrations.Migration):
    dependencies = [
        ("wps", "0008_wps_revision_and_approval_flow"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wps",
            name="revision_number",
            field=models.IntegerField(default=0),
        ),
        migrations.RunPython(resequence_revisions, migrations.RunPython.noop),
    ]
