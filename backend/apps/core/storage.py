
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class MinIOStorage(S3Boto3Storage):
    """Custom MinIO storage with security defaults."""

    location = 'media'
    file_overwrite = False
    default_acl = 'private'
    signature_version = 's3v4'

    def url(self, name, parameters=None, expire=None, http_method=None):
        """Generate presigned URL for private files."""
        return super().url(name, parameters, expire, http_method)


class LocalStorage(FileSystemStorage):
    """Local file storage for development."""

    pass
