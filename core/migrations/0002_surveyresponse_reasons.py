from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Add the new M2M field
        migrations.AddField(
            model_name='surveyresponse',
            name='reasons',
            field=models.ManyToManyField(blank=True, to='core.reason'),
        ),
        # Remove the old FK field
        migrations.RemoveField(
            model_name='surveyresponse',
            name='reason',
        ),
    ]
