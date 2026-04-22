from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stories", "0004_storyaccess"),
    ]

    operations = [
        migrations.AddField(
            model_name="storyaccess",
            name="view_counted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
