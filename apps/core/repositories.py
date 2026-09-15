from apps.core.models import Operation

class OperationRepository:
    def create(self, user, key, fingerprint):
        return Operation.objects.create(user=user, key=key, fingerprint=fingerprint)

    def get(self, user, key):
        return Operation.objects.filter(user=user, key=key).first()

    def complete(self, operation, response):
        operation.response = response
        operation.save(update_fields=['response'])
