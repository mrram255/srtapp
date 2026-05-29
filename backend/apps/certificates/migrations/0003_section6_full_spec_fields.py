# Section 6 full spec fields

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0002_certificate_workflow'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='certificatetemplate',
            name='auto_generate',
            field=models.BooleanField(default=False, help_text='When true, approved requests can be issued automatically on approval.'),
        ),
        migrations.AddField(
            model_name='certificatetemplate',
            name='footer_image',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='certificatetemplate',
            name='header_image',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='certificatetemplate',
            name='variables',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='certificaterequest',
            name='fee_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10),
        ),
        migrations.AddField(
            model_name='certificaterequest',
            name='fee_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='certificaterequest',
            name='generated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='certificaterequest',
            name='number_of_copies',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='certificaterequest',
            name='rejected_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='certificaterequest',
            name='remarks',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='certificaterequest',
            name='request_number',
            field=models.CharField(blank=True, db_index=True, max_length=32, unique=True),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='certificate_number',
            field=models.CharField(blank=True, db_index=True, max_length=32, unique=True),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='data_snapshot',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='download_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='is_revoked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='qr_verification_url',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='revoked_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='revoked_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='revoked_certificates',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='revoked_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='valid_until',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='certificatetemplate',
            name='certificate_type',
            field=models.CharField(
                choices=[
                    ('bonafide', 'Bonafide'),
                    ('character', 'Character'),
                    ('attendance', 'Attendance'),
                    ('transfer', 'Transfer Certificate'),
                    ('migration', 'Migration'),
                    ('provisional', 'Provisional'),
                    ('medium_of_instruction', 'Medium of Instruction'),
                    ('conduct', 'Conduct'),
                    ('noc', 'NOC'),
                    ('transcript', 'Transcript'),
                    ('degree', 'Degree'),
                    ('id_card', 'ID Card'),
                    ('custom', 'Custom'),
                    ('other', 'Other'),
                ],
                default='bonafide',
                max_length=32,
            ),
        ),
    ]
