"""
Services module for Sevai Hub backend.
Contains email, cache, SMS, and storage services.
"""

from app.services.cache_service import (
    cache_get,
    cache_set,
    cache_delete,
    cache_clear_pattern,
    get_redis,
    close_redis,
)
from app.services.email_service import (
    send_email,
    send_password_reset_email,
    send_technician_assignment_email,
)
from app.services.sms_service import (
    send_sms,
    send_technician_assignment_sms,
    send_verification_code_sms,
    send_service_update_sms,
)
from app.services.storage_service import (
    upload_file,
    download_file,
    delete_file,
    upload_profile_picture,
    upload_service_document,
    upload_technician_certificate,
    list_files,
)

__all__ = [
    # Cache
    "cache_get",
    "cache_set",
    "cache_delete",
    "cache_clear_pattern",
    "get_redis",
    "close_redis",
    # Email
    "send_email",
    "send_password_reset_email",
    "send_technician_assignment_email",
    # SMS
    "send_sms",
    "send_technician_assignment_sms",
    "send_verification_code_sms",
    "send_service_update_sms",
    # Storage
    "upload_file",
    "download_file",
    "delete_file",
    "upload_profile_picture",
    "upload_service_document",
    "upload_technician_certificate",
    "list_files",
]
