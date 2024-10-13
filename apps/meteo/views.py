from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.meteo.models import Cyclone, Inondation, Secheresse, AutreCatastrophe, TremblementDeTerre, Tsunami, Degats
from apps.meteo.serializers import CycloneSerializer, InondationSerializer, SecheresseSerializer, AutreCatastropheSerializer, TremblementDeTerreSerializer, TsunamiSerializer, DegatsSerializer

class CatastropheListView(APIView):

    def get(self, request):
        # Récupérer toutes les instances des catastrophes
        cyclones = Cyclone.objects.all().order_by('-id_cyclone')
        inondations = Inondation.objects.all().order_by('-id_inondation')
        secheresses = Secheresse.objects.all().order_by('-id_secheresse')
        autres_catastrophes = AutreCatastrophe.objects.all()
        tremblements_de_terre = TremblementDeTerre.objects.all()
        tsunamis = Tsunami.objects.all()
        degats = Degats.objects.all()

        # Sérialiser les données
        cyclones_serializer = CycloneSerializer(cyclones, many=True)
        inondations_serializer = InondationSerializer(inondations, many=True)
        secheresses_serializer = SecheresseSerializer(secheresses, many=True)
        autres_catastrophes_serializer = AutreCatastropheSerializer(autres_catastrophes, many=True)
        tremblements_de_terre_serializer = TremblementDeTerreSerializer(tremblements_de_terre, many=True)
        tsunamis_serializer = TsunamiSerializer(tsunamis, many=True)
        degats_serializer = DegatsSerializer(degats, many=True)

        # Organiser les données dans une structure unifiée
        data = {
            "cyclones": cyclones_serializer.data,
            "inondations": inondations_serializer.data,
            "secheresses": secheresses_serializer.data,
            "autres_catastrophes": autres_catastrophes_serializer.data,
            "tremblements_de_terre": tremblements_de_terre_serializer.data,
            "tsunamis": tsunamis_serializer.data,
            "degats": degats_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)
