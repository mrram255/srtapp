from django.db import migrations

from apps.users.rbac_seed import seed_rbac, unseed_rbac


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_rbac, unseed_rbac),
    ]
