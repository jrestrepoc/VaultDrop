"""Transactional idempotency for mutations. No HTTP types in this service."""
import hashlib
import json
from uuid import UUID, uuid4
from django.db import IntegrityError, transaction
from apps.core.domain import BusinessError, ConflictError
from apps.core.repositories import OperationRepository

class OperationService:
    def __init__(self, repository=None):
        self.repository = repository or OperationRepository()

    def execute(self, user, key, command, payload, action):
        try:
            key = UUID(str(key)) if key else uuid4()
        except (ValueError, TypeError, AttributeError) as exc:
            raise BusinessError('Idempotency-Key debe ser un UUID.') from exc
        fingerprint = hashlib.sha256(json.dumps([command, payload], sort_keys=True, default=str).encode()).hexdigest()
        try:
            with transaction.atomic():
                # Claim before business reads. Concurrent duplicates wait for commit.
                operation = self.repository.create(user, key, fingerprint)
                response = action()
                self.repository.complete(operation, response)
                return response
        except IntegrityError:
            previous = self.repository.get(user, key)
            if previous is None:
                raise
            if previous.fingerprint != fingerprint:
                raise ConflictError('Esta clave ya se utilizó para otra operación.')
            return previous.response
