# Generated for Section 6 certificate workflow

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0001_initial'),
        ('students', '0006_student_json_profile_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='certificatetemplate',
            name='html_body',
            field=models.TextField(blank=True, help_text='Optional HTML override; default Django template used when empty.'),
        ),
        migrations.AddField(
            model_name='certificatetemplate',
            name='requires_approval',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='certificatetemplate',
            name='certificate_type',
            field=models.CharField(
                choices=[
                    ('transcript', 'Transcript'),
                    ('degree', 'Degree Certificate'),
                    ('provisional', 'Provisional Certificate'),
                    ('bonafide', 'Bonafide Certificate'),
                    ('id_card', 'ID Card'),
                    ('other', 'Other'),
                ],
                default='other',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name='certificatetemplate',
            name='template_file',
            field=models.FileField(blank=True, upload_to='certificates/templates/'),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='blockchain_hash',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='pdf_url',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='qr_payload',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='verification_code',
            field=models.CharField(blank=True, db_index=True, max_length=32, unique=True),
        ),
        migrations.CreateModel(
            name='CertificateRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('purpose', models.TextField(blank=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pending'),
                            ('approved', 'Approved'),
                            ('rejected', 'Rejected'),
                            ('issued', 'Issued'),
                            ('cancelled', 'Cancelled'),
                        ],
                        db_index=True,
                        default='pending',
                        max_length=16,
                    ),
                ),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('review_remarks', models.TextField(blank=True)),
                (
                    'requested_by',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='certificate_requests_made',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'reviewed_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='certificate_requests_reviewed',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'student',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='certificate_requests',
                        to='students.student',
                    ),
                ),
                (
                    'template',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='requests',
                        to='certificates.certificatetemplate',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='%(app_label)s_%(class)s_created',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'updated_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='%(app_label)s_%(class)s_updated',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'db_table': 'certificates_requests',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterField(
            model_name='certificateissue',
            name='download_url',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='certificateissue',
            name='request',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='certificate_issue',
                to='certificates.certificaterequest',
            ),
        ),
    ]
