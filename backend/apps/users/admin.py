from django.contrib import admin

from apps.users.models import Module, ModulePermission, Role, RolePermission, UserActivity

admin.site.register(Role)
admin.site.register(Module)
admin.site.register(ModulePermission)
admin.site.register(RolePermission)
admin.site.register(UserActivity)
