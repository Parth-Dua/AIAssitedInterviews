"""Wires up the (in-memory) repositories and services shared across
routers. There's no database or DI framework here, so this module just
owns the singleton instances every route depends on.
"""

from app.repositories.document_repository import DocumentRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.user_repository import UserRepository
from app.services.document_service import DocumentService
from app.services.membership_service import MembershipService
from app.services.permission_service import PermissionService

user_repository = UserRepository()
membership_repository = MembershipRepository()
document_repository = DocumentRepository()

permission_service = PermissionService(membership_repository)
document_service = DocumentService(document_repository, permission_service)
membership_service = MembershipService(membership_repository)
