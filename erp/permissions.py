from rest_framework.permissions import BasePermission, SAFE_METHODS
from customers.models import Customer

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'manager']

class StaffCanWriteNoDelete(BasePermission):
    """
    - Admin/Manager: full access (including DELETE)
    - Staff: can read, create, update (POST, PUT, PATCH) but NOT DELETE
    - Others (Wholesaler/Customer): no write access
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = request.user.role
        if role in ['admin', 'manager']:
            return True
        if role == 'staff':
            if request.method == 'DELETE':
                return False
            return True
        return False

class IsOwnerOrHigher(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        role = user.role
        if role in ['admin', 'manager']:
            return True
        if role == 'staff':
            # Staff can read/write any object, but delete is blocked elsewhere
            return True
        # For wholesaler/customer: only own objects
        if hasattr(obj, 'collector') and obj.collector == user:
            return True
        if hasattr(obj, 'customer') and obj.customer and obj.customer.ref_by == user:
            return True
        if isinstance(obj, Customer) and obj.ref_by == user:
            return True
        return False