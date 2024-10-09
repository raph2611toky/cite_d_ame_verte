from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser

from django.db import transaction

from apps.evenements.models import Evenement, Emplacement, ImageEvenement, FileEvenement
from apps.evenements.serializers import EvenementSerializer
from config.helpers.permissions import IsAuthenticatedUserOrClient
from config.helpers.authentications import UserOrClientAuthentication


class EvenementListView(APIView):
    authentication_classes = [UserOrClientAuthentication]
    permission_classes = [IsAuthenticatedUserOrClient]

    def get(self, request):
        try:
            evenements = Evenement.objects.all()
            serializer = EvenementSerializer(evenements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EvenementProfileFindView(APIView):
    authentication_classes = [UserOrClientAuthentication]
    permission_classes = [IsAuthenticatedUserOrClient]

    def get(self, request, pk):
        try:
            evenement = get_object_or_404(Evenement, pk=pk)
            serializer = EvenementSerializer(evenement)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EvenementProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def put(self, request, pk):
        # request.FILES = ['images','files']
        # request.body = ['name_evenement','description','date_debut','date_fin','type', 'organisateurs','participants','emplacement']
        try:
            evenement = get_object_or_404(Evenement, pk=pk)
            
            if request.user not in evenement.organisateurs.all():
                return Response({'erreur': 'Vous n\'êtes pas autorisé à modifier cet événement'}, status=status.HTTP_403_FORBIDDEN)
            evenement_serializer = EvenementSerializer(evenement, data=request.data, partial=True)

            if evenement_serializer.is_valid():
                evenement = evenement_serializer.save()
                if 'images' in request.FILES:
                    images = request.FILES.getlist('images')
                    for image in images:
                        ImageEvenement.objects.create(image=image, evenement=evenement)
                if 'files' in request.FILES:
                    files = request.FILES.getlist('files')
                    for file in files:
                        FileEvenement.objects.create(file=file, evenement=evenement)

                return Response(evenement_serializer.data, status=status.HTTP_200_OK)
            return Response(evenement_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            evenement = get_object_or_404(Evenement, pk=pk)
            evenement.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'erreur':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EvenementNewView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def validate_data(self, data):
        keys = ['name_evenement', 'description', 'date_debut', 'date_fin', 'type', 'name_emplacement', 'longitude', 'latitude']
        if any(key not in data.keys() for key in keys):
            return False
        return True
    
    def post(self, request):
        try:
            print(request.data)
            if not self.validate_data(request.data):
                return Response({'erreur': 'Tous les champs sont requis'}, status=status.HTTP_400_BAD_REQUEST)

            evenement_data = request.data.copy()

            name_emplacement = evenement_data.pop('name_emplacement', "Inconu")
            latitude = evenement_data.pop('latitude')
            longitude = evenement_data.pop('longitude')

            if isinstance(latitude, list):
                latitude = latitude[0]
            if isinstance(longitude, list):
                longitude = longitude[0]
            if isinstance(name_emplacement, list):
                name_emplacement = name_emplacement[0]

            latitude = float(latitude)
            longitude = float(longitude)
            
            with transaction.atomic():
                emplacement, created = Emplacement.objects.get_or_create(
                    latitude=latitude,
                    longitude=longitude,
                    defaults={'name_emplacement': name_emplacement}
                )
                print('emplacement is created .....')
                evenement_data['emplacement'] = emplacement
                print(evenement_data)
                evenement_serializer = EvenementSerializer(data=evenement_data, context={'evenement_data': evenement_data})

                if evenement_serializer.is_valid():
                    print('evenement valid .....')
                    evenement_save = evenement_serializer.save()
                    evenement = Evenement.objects.get(id_evenement=evenement_save.id_evenement)
                    evenement.organisateurs.add(request.user.id)
                    evenement.save()
                    print('organisers added...')
            images = request.FILES.getlist('images')
            for image in images:
                ImageEvenement.objects.create(image=image, evenement=evenement)

            files = request.FILES.getlist('files')
            for file in files:
                FileEvenement.objects.create(file=file, evenement=evenement)

            return Response(evenement_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({'erreur': str(e)}, status=status.HTTP_400_BAD_REQUEST)


