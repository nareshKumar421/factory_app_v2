# gate_core/services/lock_manager.py

def ensure_editable(instance):
    if instance.is_locked:
        raise PermissionError("This record is locked and cannot be modified.")
    return True