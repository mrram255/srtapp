# Generated manually for Section 5 profile depth

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_add_mentor_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='family_details',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='student',
            name='education_details',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='student',
            name='permanent_address',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='student',
            name='correspondence_address',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='student',
            name='is_address_same',
            field=models.BooleanField(default=True),
        ),
    ]
