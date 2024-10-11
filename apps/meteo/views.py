from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.meteo.models import Cyclone, Inondation, Secheresse, AutreCatastrophe
from apps.meteo.serializers import CycloneSerializer, InondationSerializer, SecheresseSerializer, AutreCatastropheSerializer

class CatastropheListView(APIView):

    def get(self, request):
        cyclones = Cyclone.objects.all()
        inondations = Inondation.objects.all()
        secheresses = Secheresse.objects.all()
        autres_catastrophes = AutreCatastrophe.objects.all()

        cyclones_serializer = CycloneSerializer(cyclones, many=True)
        inondations_serializer = InondationSerializer(inondations, many=True)
        secheresses_serializer = SecheresseSerializer(secheresses, many=True)
        autres_catastrophes_serializer = AutreCatastropheSerializer(autres_catastrophes, many=True)

        data = {
            "cyclones": cyclones_serializer.data,
            "inondations": inondations_serializer.data,
            "secheresses": secheresses_serializer.data,
            "autres_catastrophes": autres_catastrophes_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)
