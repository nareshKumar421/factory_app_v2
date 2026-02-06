# Accounts Permissions

## Overview

The Accounts module uses Django's built-in permission system for access control. Permissions are defined at the model level and enforced via DRF permission classes.

---

## Permission List

### User Permissions

| Permission Codename | Description | Usage |
|---------------------|-------------|-------|
| `accounts.can_create_user` | Can create user | Creating new user accounts |
| `accounts.can_view_user` | Can view user | Viewing user details and list |
| `accounts.can_edit_user` | Can edit user | Modifying user information |
| `accounts.can_delete_user` | Can delete user | Removing user accounts |
| `accounts.can_manage_user_permissions` | Can manage user permissions | Assigning/removing permissions |

### Department Permissions

| Permission Codename | Description | Usage |
|---------------------|-------------|-------|
| `accounts.can_view_department` | Can view department | Viewing department list and details |
| `accounts.can_manage_department` | Can manage department | Creating, editing, deleting departments |

---

## Permission Classes

### Individual Permission Classes

```python
from accounts.permissions import (
    CanCreateUser,
    CanViewUser,
    CanEditUser,
    CanDeleteUser,
    CanManageUserPermissions,
    CanViewDepartment,
    CanManageDepartment,
)
```

### Combined Permission Classes

```python
from accounts.permissions import CanManageUser

# CanManageUser automatically checks:
# - POST requests: can_create_user
# - PUT/PATCH requests: can_edit_user
# - DELETE requests: can_delete_user
# - GET requests: can_view_user
```

---

## Usage Examples

### In Views

```python
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import CanViewUser, CanCreateUser

class UserListView(APIView):
    permission_classes = [IsAuthenticated, CanViewUser]

    def get(self, request):
        # List users
        pass

class UserCreateView(APIView):
    permission_classes = [IsAuthenticated, CanCreateUser]

    def post(self, request):
        # Create user
        pass
```

### In ViewSets

```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import CanManageUser

class UserViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, CanManageUser]
    # Permissions auto-applied based on action (list, create, update, delete)
```

### With Company Context

```python
from rest_framework.permissions import IsAuthenticated
from company.permissions import HasCompanyContext
from accounts.permissions import CanViewUser

class UserListView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewUser]
```

---

## Assigning Permissions

### Via Django Admin

1. Go to **Admin > Users > [Select User]**
2. Scroll to **User permissions** section
3. Add permissions from the available list

### Via Code

```python
from django.contrib.auth.models import Permission
from accounts.models import User

user = User.objects.get(email='user@example.com')

# Add permission
permission = Permission.objects.get(codename='can_view_user')
user.user_permissions.add(permission)

# Remove permission
user.user_permissions.remove(permission)

# Check permission
user.has_perm('accounts.can_view_user')  # Returns True/False
```

### Via Groups

```python
from django.contrib.auth.models import Group, Permission

# Create group with permissions
group = Group.objects.create(name='User Managers')
permissions = Permission.objects.filter(
    codename__in=['can_create_user', 'can_view_user', 'can_edit_user']
)
group.permissions.set(permissions)

# Add user to group
user.groups.add(group)
```

---

## Permission Check Flow

```
Request
   │
   ▼
┌──────────────────┐
│  IsAuthenticated │──► Is user logged in?
└────────┬─────────┘
         │ Yes
         ▼
┌──────────────────┐
│ HasCompanyContext│──► Is Company-Code header valid?
└────────┬─────────┘
         │ Yes
         ▼
┌──────────────────┐
│  CanViewUser     │──► Does user have permission?
└────────┬─────────┘
         │ Yes
         ▼
    Access Granted
```

---

## API Endpoints & Required Permissions

| Endpoint | Method | Required Permission |
|----------|--------|---------------------|
| `/users/` | GET | `can_view_user` |
| `/users/` | POST | `can_create_user` |
| `/users/<id>/` | GET | `can_view_user` |
| `/users/<id>/` | PUT/PATCH | `can_edit_user` |
| `/users/<id>/` | DELETE | `can_delete_user` |
| `/users/<id>/permissions/` | GET/PUT | `can_manage_user_permissions` |
| `/departments/` | GET | `can_view_department` |
| `/departments/` | POST | `can_manage_department` |
| `/departments/<id>/` | PUT/PATCH/DELETE | `can_manage_department` |

---

## Notes

- **Superusers** bypass all permission checks
- **Self-access**: Users can always view/edit their own profile (restricted fields)
- **Self-delete**: Users cannot delete their own account
- Permissions are stored in Django's `auth_permission` table
- Use `user.get_all_permissions()` to get all permissions including from groups
