from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
        ("wps", "0007_wps_equipment"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="wps",
            name="wps_project_code_unique",
        ),
        migrations.AddField(
            model_name="wps",
            name="approved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wps",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="wps_approved_set",
                to="users.user",
            ),
        ),
        migrations.AddField(
            model_name="wps",
            name="is_current",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="wps",
            name="revision_number",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="wps",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wps",
            name="reviewed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="wps_reviewed_set",
                to="users.user",
            ),
        ),
        migrations.AddField(
            model_name="wps",
            name="root_wps",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="revisions",
                to="wps.wps",
            ),
        ),
        migrations.AddField(
            model_name="wps",
            name="submitted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="wps",
            name="submitted_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="wps_submitted_set",
                to="users.user",
            ),
        ),
        migrations.AddConstraint(
            model_name="wps",
            constraint=models.UniqueConstraint(
                fields=("project", "code", "revision_number"),
                name="wps_project_code_revision_unique",
            ),
        ),
    ]
