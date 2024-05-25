from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Account, Destination
from .Serializers import AccountSerializer, DestinationSerializer
import requests

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

@api_view(['GET'])
def get_destinations_by_account(request, account_id):
    try:
        account = Account.objects.get(account_id=account_id)
        destinations = account.destinations.all()
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def handle_incoming_data(request):
    secret_token = request.headers.get('CL-X-TOKEN')
    if not secret_token:
        return Response({'error': 'Un Authenticate'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        account = Account.objects.get(app_secret_token=secret_token)
    except Account.DoesNotExist:
        return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data
    if request.method == 'POST':
        destinations = account.destinations.all()
        for destination in destinations:
            headers = destination.headers
            url = destination.url
            method = destination.http_method.lower()

            if method == 'get':
                response = requests.get(url, headers=headers, params=data)
            elif method in ['post', 'put']:
                response = getattr(requests, method)(url, headers=headers, json=data)
            else:
                return Response({'error': 'Invalid HTTP method'}, status=status.HTTP_400_BAD_REQUEST)

            if not response.ok:
                return Response({'error': 'Failed to send data to destination'}, status=response.status_code)

        return Response({'status': 'Data sent successfully'}, status=status.HTTP_200_OK)

    return Response({'error': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
