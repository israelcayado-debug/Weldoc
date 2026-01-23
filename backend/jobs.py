from apps.integrations import models as integration_models
from apps.integrations.views import IntegrationEventViewSet


def deliver_webhooks_batch():
    viewset = IntegrationEventViewSet()
    return viewset.deliver_queue(request=None)
