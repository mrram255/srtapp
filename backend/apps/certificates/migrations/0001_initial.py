import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('colleges', '0001_initial'),
        ('accounts', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateTemplate',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates_certificatetemplate_created', to='accounts.user')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates_certificatetemplate_updated', to='accounts.user')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=64, unique=True)),
                ('description', models.TextField(blank=True)),
                ('certificate_type', models.CharField(choices=[('transcript', 'Transcript'), ('degree', 'Degree Certificate'), ('provisional', 'Provisional Certificate'), ('id_card', 'ID Card'), ('other', 'Other')], default='other', max_length=32)),
                ('template_file', models.FileField(upload_to='certificates/templates/')),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificate_templates', to='colleges.college')),
            ],
            options={
                'db_table': 'certificates_templates',
                'verbose_name': 'Certificate Template',
                'verbose_name_plural': 'Certificate Templates',
                'ordering': ['order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CertificateIssue',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates_certificateissue_created', to='accounts.user')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates_certificateissue_updated', to='accounts.user')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('issued', 'Issued'), ('rejected', 'Rejected')], default='pending', max_length=16)),
                ('issued_at', models.DateTimeField(blank=True, null=True)),
                ('download_url', models.URLField(blank=True)),
                ('remarks', models.TextField(blank=True)),
                ('issued_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issued_certificates', to='accounts.user')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificate_issues', to='students.student')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='issues', to='certificates.certificatetemplate')),
            ],
            options={
                'db_table': 'certificates_issues',
                'verbose_name': 'Certificate Issue',
                'verbose_name_plural': 'Certificate Issues',
                'ordering': ['-created_at'],
            },
        ),
    ]
