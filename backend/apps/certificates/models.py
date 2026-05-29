import uuid

from django.db import models

from apps.core.models import OrderedModel, TimeStampedModel


class CertificateTemplate(OrderedModel):
    class CertificateType(models.TextChoices):
        BONAFIDE = 'bonafide', 'Bonafide'
        CHARACTER = 'character', 'Character'
        ATTENDANCE = 'attendance', 'Attendance'
        TRANSFER = 'transfer', 'Transfer Certificate'
        MIGRATION = 'migration', 'Migration'
        PROVISIONAL = 'provisional', 'Provisional'
        MEDIUM_OF_INSTRUCTION = 'medium_of_instruction', 'Medium of Instruction'
        CONDUCT = 'conduct', 'Conduct'
        NOC = 'noc', 'NOC'
        TRANSCRIPT = 'transcript', 'Transcript'
        DEGREE = 'degree', 'Degree'
        ID_CARD = 'id_card', 'ID Card'
        CUSTOM = 'custom', 'Custom'
        OTHER = 'other', 'Other'

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        related_name='certificate_templates',
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    certificate_type = models.CharField(
        max_length=32,
        choices=CertificateType.choices,
        default=CertificateType.BONAFIDE,
    )
    template_file = models.FileField(upload_to='certificates/templates/', blank=True)
    html_body = models.TextField(
        blank=True,
        help_text='HTML template with {{variables}}; uses default layout when empty.',
    )
    header_image = models.CharField(max_length=500, blank=True)
    footer_image = models.CharField(max_length=500, blank=True)
    variables = models.JSONField(default=list, blank=True)
    requires_approval = models.BooleanField(default=True)
    auto_generate = models.BooleanField(
        default=False,
        help_text='When true, approved requests can be issued automatically on approval.',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'certificates_templates'
        verbose_name = 'Certificate Template'
        verbose_name_plural = 'Certificate Templates'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


class CertificateRequest(TimeStampedModel):
    class RequestStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        GENERATED = 'generated', 'Generated'
        ISSUED = 'issued', 'Issued'
        CANCELLED = 'cancelled', 'Cancelled'

    request_number = models.CharField(max_length=32, unique=True, db_index=True, blank=True)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='certificate_requests',
    )
    template = models.ForeignKey(
        CertificateTemplate,
        on_delete=models.PROTECT,
        related_name='requests',
    )
    requested_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='certificate_requests_made',
    )
    purpose = models.TextField(blank=True)
    number_of_copies = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=16,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
        db_index=True,
    )
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificate_requests_reviewed',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_remarks = models.TextField(blank=True)
    rejected_reason = models.TextField(blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fee_paid = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'certificates_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.request_number} — {self.student.enrollment_number} ({self.status})'


class CertificateIssue(TimeStampedModel):
    """Issued certificate record (spec: IssuedCertificate)."""

    class CertificateStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ISSUED = 'issued', 'Issued'
        REJECTED = 'rejected', 'Rejected'
        REVOKED = 'revoked', 'Revoked'

    request = models.OneToOneField(
        CertificateRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificate_issue',
    )
    certificate_number = models.CharField(max_length=32, unique=True, db_index=True, null=True, blank=True)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='certificate_issues',
    )
    template = models.ForeignKey(
        CertificateTemplate,
        on_delete=models.PROTECT,
        related_name='issues',
    )
    issued_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='issued_certificates',
    )
    status = models.CharField(
        max_length=16,
        choices=CertificateStatus.choices,
        default=CertificateStatus.PENDING,
    )
    issued_at = models.DateTimeField(null=True, blank=True)
    download_url = models.CharField(max_length=500, blank=True)
    pdf_url = models.CharField(max_length=500, blank=True)
    qr_verification_url = models.CharField(max_length=500, blank=True)
    verification_code = models.CharField(max_length=32, unique=True, db_index=True, null=True, blank=True)
    blockchain_hash = models.CharField(max_length=64, blank=True)
    qr_payload = models.CharField(max_length=255, blank=True)
    data_snapshot = models.JSONField(default=dict, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    is_revoked = models.BooleanField(default=False)
    revoked_reason = models.TextField(blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_certificates',
    )
    download_count = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'certificates_issues'
        verbose_name = 'Certificate Issue'
        verbose_name_plural = 'Certificate Issues'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = uuid.uuid4().hex[:16].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        label = self.certificate_number or self.verification_code
        return f'{label} — {self.student.enrollment_number}'
