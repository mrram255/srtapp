from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0003_section6_full_spec_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificateissue',
            name='certificate_number',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='certificateissue',
            name='verification_code',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True, unique=True),
        ),
    ]
