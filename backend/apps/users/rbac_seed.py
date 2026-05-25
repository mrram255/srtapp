from __future__ import annotations

MODULES = [
    ('dashboard', 'Dashboard', 'layout-dashboard', 1),
    ('users', 'User Management', 'users', 2),
    ('students', 'Students', 'graduation-cap', 3),
    ('teachers', 'Teachers', 'users', 4),
    ('academics', 'Academics', 'book-open', 5),
    ('attendance', 'Attendance', 'calendar-check', 6),
    ('exams', 'Examinations', 'file-text', 7),
    ('finance', 'Finance', 'dollar-sign', 8),
    ('admissions', 'Admissions', 'school', 9),
    ('library', 'Library', 'library', 10),
    ('hostel', 'Hostel', 'bed', 11),
    ('transport', 'Transport', 'bus', 12),
    ('placements', 'Placements', 'briefcase', 13),
    ('reports', 'Reports', 'bar-chart', 14),
    ('settings', 'Settings', 'settings', 15),
]

ACTIONS = ['view', 'create', 'edit', 'delete', 'export', 'import', 'approve']

ROLES = [
    ('super_admin', 'Super Admin', True),
    ('principal', 'Principal', True),
    ('vice_principal', 'Vice Principal', True),
    ('dean', 'Dean', True),
    ('registrar', 'Registrar', True),
    ('bursar', 'Bursar', True),
    ('chief_accountant', 'Chief Accountant', True),
    ('accountant', 'Accountant', True),
    ('cashier', 'Cashier', True),
    ('coe', 'Controller of Examinations', True),
    ('exam_staff', 'Exam Staff', True),
    ('admission_officer', 'Admission Officer', True),
    ('admission_counsellor', 'Admission Counsellor', True),
    ('hod', 'Head of Department', True),
    ('teacher', 'Teacher', True),
    ('librarian', 'Librarian', True),
    ('hostel_warden', 'Hostel Warden', True),
    ('placement_officer', 'Placement Officer', True),
    ('nss_officer', 'NSS Officer', True),
    ('sports_officer', 'Sports Officer', True),
    ('student', 'Student', True),
    ('parent', 'Parent', True),
    ('counsellor', 'Counsellor', True),
    ('security_officer', 'Security Officer', True),
    ('store_keeper', 'Store Keeper', True),
    ('it_support', 'IT Support', True),
    ('naac_coordinator', 'NAAC Coordinator', True),
    ('research_coordinator', 'Research Coordinator', True),
]

ROLE_MODULE_ACTIONS = {
    'super_admin': 'all',
    'principal': {
        'dashboard': ['view', 'export', 'approve'],
        'users': ['view'],
        'students': ['view', 'export', 'approve'],
        'teachers': ['view', 'export'],
        'academics': ['view', 'approve'],
        'attendance': ['view', 'export'],
        'exams': ['view', 'approve'],
        'finance': ['view', 'export'],
        'admissions': ['view', 'approve'],
        'reports': ['view', 'export'],
        'settings': ['view'],
    },
    'teacher': {
        'dashboard': ['view'],
        'students': ['view'],
        'academics': ['view', 'edit'],
        'attendance': ['view', 'create', 'edit'],
        'exams': ['view', 'edit'],
    },
    'student': {
        'dashboard': ['view'],
        'academics': ['view'],
        'attendance': ['view'],
        'exams': ['view'],
        'finance': ['view'],
        'library': ['view'],
    },
    'parent': {
        'dashboard': ['view'],
        'students': ['view'],
        'attendance': ['view'],
        'finance': ['view'],
        'exams': ['view'],
    },
    'accountant': {
        'dashboard': ['view'],
        'finance': ['view', 'create', 'edit', 'export'],
        'students': ['view'],
    },
    'librarian': {
        'dashboard': ['view'],
        'library': ['view', 'create', 'edit', 'delete', 'export', 'import'],
    },
    'hod': {
        'dashboard': ['view'],
        'students': ['view', 'edit', 'export'],
        'teachers': ['view'],
        'academics': ['view', 'edit', 'approve'],
        'attendance': ['view', 'export', 'approve'],
        'exams': ['view', 'approve'],
    },
    'admission_officer': {
        'dashboard': ['view'],
        'admissions': ['view', 'create', 'edit', 'delete', 'export', 'import', 'approve'],
    },
}


def seed_rbac(apps, schema_editor):
    Module = apps.get_model('users', 'Module')
    ModulePermission = apps.get_model('users', 'ModulePermission')
    Role = apps.get_model('users', 'Role')
    RolePermission = apps.get_model('users', 'RolePermission')

    module_map = {}
    for name, display_name, icon, order in MODULES:
        module_map[name] = Module.objects.create(
            name=name,
            display_name=display_name,
            icon=icon,
            order=order,
        )

    permission_map = {}
    for module_name, module in module_map.items():
        for action in ACTIONS:
            perm = ModulePermission.objects.create(module=module, action=action)
            permission_map[(module_name, action)] = perm

    for name, display_name, is_system in ROLES:
        role = Role.objects.create(
            name=name,
            display_name=display_name,
            description=f'System role: {display_name}',
            is_system_role=is_system,
        )
        module_actions = ROLE_MODULE_ACTIONS.get(name)
        if module_actions == 'all':
            assigned = list(permission_map.values())
        elif module_actions:
            assigned = [
                permission_map[(module_name, action)]
                for module_name, actions in module_actions.items()
                for action in actions
                if (module_name, action) in permission_map
            ]
        else:
            assigned = [permission_map[('dashboard', 'view')]]
        for perm in assigned:
            RolePermission.objects.create(role=role, module_permission=perm)


def unseed_rbac(apps, schema_editor):
    RolePermission = apps.get_model('users', 'RolePermission')
    Role = apps.get_model('users', 'Role')
    ModulePermission = apps.get_model('users', 'ModulePermission')
    Module = apps.get_model('users', 'Module')
    RolePermission.objects.all().delete()
    Role.objects.all().delete()
    ModulePermission.objects.all().delete()
    Module.objects.all().delete()
