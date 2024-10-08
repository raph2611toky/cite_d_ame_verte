from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.evenements.models import Evenement
from apps.evenements.serializers import EvenementSerializer
from apps.client.permissions import IsAuthenticatedClient


class EvenementListView(APIView):
    permission_classes = [IsAuthenticated | IsAuthenticatedClient]

    def get(self, request):
        try:
            evenements = Evenement.objects.all()
            serializer = EvenementSerializer(evenements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EvenementProfileView(APIView):
    permission_classes = [IsAuthenticated | IsAuthenticatedClient]

    def get(self, request, pk):
        try:
            evenement = get_object_or_404(Evenement, pk=pk)
            serializer = EvenementSerializer(evenement)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            # request.body = ['name_evenement','description','date_debut','date_fin','type', 'organisateurs','participants','emplacement','images','files']
            evenement = get_object_or_404(Evenement, pk=pk)
            serializer = EvenementSerializer(evenement, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            retun Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            evenement = get_object_or_404(Evenement, pk=pk)
            evenement.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EvenementNewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # request.body = ['name_evenement','description','date_debut','date_fin','type', 'organisateurs','participants','emplacement','images','files']
        try:
            serializer = EvenementSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            retun Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)
