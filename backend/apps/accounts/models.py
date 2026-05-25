import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


ROLE_CHOICES = [
    ('SUPER_ADMIN', 'Super Admin'),
    ('ADMIN', 'Admin'),
    ('HOD', 'Head of Department'),
    ('TEACHER', 'Teacher'),
    ('STUDENT', 'Student'),
    ('PARENT', 'Parent'),
    ('ACCOUNTANT', 'Accountant'),
    ('LIBRARIAN', 'Librarian'),
    ('SECURITY', 'Security'),
]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, phone, first_name, last_name, role, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not phone:
            raise ValueError('Phone is required')
        if not first_name or not last_name:
            raise ValueError('First and last name are required')
        if not role:
            raise ValueError('Role is required')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            role=role,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, first_name, last_name, password=None, **extra_fields):
        # Django's createsuperuser passes `role=` as a kwarg; we also pass role below — pop to avoid collision.
        extra_fields.pop('role', None)

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        return self.create_user(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            role='SUPER_ADMIN',
            password=password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
    )
    role = models.CharField(max_length=50, db_index=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True)
    role_ref = models.ForeignKey(
        'users.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
    )
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=1,
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        blank=True,
    )
    date_of_birth = models.DateField(null=True, blank=True)
    profile_photo = models.CharField(max_length=500, blank=True)
    signature = models.CharField(max_length=500, blank=True)
    aadhaar_number = models.CharField(max_length=255, blank=True)
    pan_number = models.CharField(max_length=255, blank=True)

    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='India', blank=True)

    joined_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_users',
    )

    is_active = models.BooleanField(default=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # Security fields
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_device = models.CharField(max_length=500, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=100, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=False)

    # Soft delete (views expect is_deleted / soft_delete)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name', 'role']

    class Meta:
        db_table = 'auth_users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['role', 'college']),
            models.Index(fields=['college', 'is_active']),
        ]
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(part for part in parts if part).strip()

    def get_full_name(self):
        return self.full_name

    def get_masked_aadhaar(self):
        from apps.core.utils import mask_aadhaar

        if not self.aadhaar_number:
            return ''
        try:
            return mask_aadhaar(self.aadhaar_number)
        except Exception:
            return 'XXXX-XXXX-XXXX'

    def get_masked_phone(self):
        if len(self.phone) <= 4:
            return self.phone
        return f'{"X" * (len(self.phone) - 4)}{self.phone[-4:]}'

    def has_module_permission(self, module: str, action: str) -> bool:
        from apps.users.services import UserService

        return UserService.check_permission(self, module, action)

    def has_field_permission(self, module: str, field: str, action: str = 'edit') -> bool:
        if self.is_superuser or self.role in {'SUPER_ADMIN'}:
            return True
        if not self.role_ref_id:
            return False
        restriction = (
            self.role_ref.role_permissions.filter(
                module_permission__module__name=module,
            )
            .values_list('field_restrictions', flat=True)
            .first()
        )
        if not restriction:
            return True
        blocked = restriction.get('hidden', []) + restriction.get('readonly', [])
        if action == 'edit' and field in blocked:
            return False
        return True

    def __str__(self):
        return f'{self.full_name} ({self.role})'

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timedelta(minutes=30)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def set_password(self, raw_password):
        super().set_password(raw_password)
        self.password_changed_at = timezone.now()
        self.must_change_password = False

    def soft_delete(self, user=None):
        """Soft-delete user record (never hard-delete from views)."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.is_active = False
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by', 'is_active'])


class ParentProfile(models.Model):
    """Extended profile for PARENT role users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile',
    )
    wards = models.ManyToManyField(
        'students.Student',
        related_name='parents',
        blank=True,
    )
    occupation = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'parent_profiles'

    def __str__(self):
        return f'Parent: {self.user.full_name}'


class OTPVerification(models.Model):
    PURPOSE_CHOICES = [
        ('email_verify', 'Email Verification'),
        ('password_reset', 'Password Reset'),
        ('two_factor', 'Two Factor Auth'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otps',
    )
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'otp_verifications'
        indexes = [
            models.Index(fields=['user', 'purpose', 'is_used']),
        ]

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    @classmethod
    def generate(cls, user, purpose):
        import random
        cls.objects.filter(user=user, purpose=purpose, is_used=False).delete()
        otp = str(random.randint(100000, 999999))
        return cls.objects.create(
            user=user,
            otp=otp,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=10),
        )
