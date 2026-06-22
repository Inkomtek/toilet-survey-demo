from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_surveyresponse_reasons'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cleaner',
            old_name='passcode',
            new_name='pin',
        ),
        migrations.AlterField(
            model_name='cleaner',
            name='pin',
            field=models.CharField(max_length=4),
        ),
    ]
