from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, DestinationViewSet, get_destinations_by_account, handle_incoming_data

router = DefaultRouter()
router.register('accounts', AccountViewSet)
router.register('destinations', DestinationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('destinations/<uuid:account_id>/', get_destinations_by_account, name='get_destinations_by_account'),
    path('server/incoming_data/', handle_incoming_data, name='handle_incoming_data'),
]
