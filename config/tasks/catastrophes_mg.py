import asyncio
import aiohttp
from aio_georss_gdacs import GdacsFeed
from googletrans import Translator
from datetime import datetime
from geopy.geocoders import Nominatim
from django.utils.timezone import make_aware
from apps.meteo.models import Location, Cyclone, Inondation, Secheresse, TremblementDeTerre, Tsunami, AutreCatastrophe, SourceDonnees


translator = Translator()

def geolocalate(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((latitude, longitude), language='en')
    if location:
        address = location.raw['address']
        city = address.get('city', '')
        country = address.get('country', '')
        return (city, country)
    else:
        return ('Inconu', 'Madagascar')

async def get_gdacs_info():
    async with aiohttp.ClientSession() as session:
        home_coordinates = (-18.7669, 46.8691)  # Coordinates of Madagascar
        feed = GdacsFeed(home_coordinates=home_coordinates, websession=session)

        status, entries = await feed.update()
        
        catastrophes = []
        if status == "OK":
            for entry in entries:
                if 'Madagascar' in entry.title or is_location_in_madagascar(entry):
                    print("Détails de la catastrophe :")
                    catastrophe = {}
                    for attr, value in vars(entry).items():
                        if hasattr(value, "__dict__"):
                            catastrophe_info = {}
                            for k, v in vars(value).items():
                                translated_value = translator.translate(str(v), src='en', dest='fr').text
                                catastrophe_info[k] = translated_value
                            catastrophe[attr] = catastrophe_info
                        else:
                            translated_value = translator.translate(str(value), src='en', dest='fr').text
                            catastrophe[attr] = translated_value
                    catastrophes.append(catastrophe)
        return catastrophes

def is_location_in_madagascar(entry):
    lat, lon = entry.coordinates
    return -25 <= lat <= -12 and 43 <= lon <= 50


def save_catastrophe(entry):
    titre = entry['_rss_entry']['_source']['title']
    description = entry['_rss_entry']['_source']['description']
    date_debut = make_aware(datetime.strptime(entry['_rss_entry']['_source']['gdacs:fromdate'], "%a, %d %b %Y %H:%M:%S GMT"))
    date_fin = make_aware(datetime.strptime(entry['_rss_entry']['_source']['gdacs:todate'], "%a, %d %b %Y %H:%M:%S GMT"))
    niveau_alerte = entry['_rss_entry']['_source']['gdacs:alertlevel']

    # Localisation
    latitude = float(entry['_rss_entry']['_source']['geo:Point']['geo:lat'])
    longitude = float(entry['_rss_entry']['_source']['geo:Point']['geo:long'])
    ville, pays = geolocalate(latitude, longitude)
    location, created = Location.objects.get_or_create(latitude=latitude, longitude=longitude, defaults={
        'ville': ville,
        'pays': pays
    })

    event_type = (entry['_rss_entry']['_source']['gdacs:eventtype']).strip()
    
    if event_type == "TC":  # Cyclone
        _,__ = Cyclone.objects.get_or_create(
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            niveau_alerte=niveau_alerte,
            location=location,
            vitesse_vent_max=float(entry['_rss_entry']['_source'].get('vitesse_vent_max', 0)),
            pression_min=float(entry['_rss_entry']['_source'].get('pression_min', 0)),
            rayon_max=float(entry['_rss_entry']['_source'].get('rayon_max', 0))
        )
        print('cyclone detected...')

    elif event_type == "FL":  # Inondation
        _,__ = Inondation.get_or_create(
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            niveau_alerte=niveau_alerte,
            location=location,
            surface_inondee=float(entry['_rss_entry']['_source'].get('surface_inondee', 0)),
            population_affectee=int(entry['_rss_entry']['_source'].get('population_affectee', 0))
        )
        print('Innondation detected.....')

    elif event_type == "DR":  # Sécheresse
        _,__ = Secheresse.get_or_create(
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            niveau_alerte=niveau_alerte,
            location=location,
            duree=int(entry['_rss_entry']['_source'].get('gdacs:durationinweek', 0)),
            surface_impactee=float(entry['_rss_entry']['_source'].get('surface_impactee', 0))
        )
        print('Sécheresse detected....')

    elif event_type == "EQ":  # Tremblement de terre
        _,__ = TremblementDeTerre.get_or_create(
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            niveau_alerte=niveau_alerte,
            location=location,
            magnitude=float(entry['_rss_entry']['_source']['gdacs:severity']['@value']),
            profondeur=float(entry['_rss_entry']['_source']['gdacs:vulnerability']['@value']),
            epicentre_latitude=latitude,
            epicentre_longitude=longitude
        )

    elif event_type == "TS":  # Tsunami
        _,__ = Tsunami.get_or_create(
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            niveau_alerte=niveau_alerte,
            location=location,
            hauteur_max_vagues=float(entry['_rss_entry']['_source'].get('hauteur_max_vagues', 0)),
            distance_parcourue=float(entry['_rss_entry']['_source'].get('distance_parcourue', 0))
        )

    else:  # Autre type de catastrophe
        _,__ = AutreCatastrophe.get_or_create(
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            niveau_alerte=niveau_alerte,
            location=location,
            type_catastrophe=event_type
        )

    ___,____ = SourceDonnees.get_or_create(
        nom_source="GDACS",
        url_source=entry['_rss_entry']['_source']['link']
    )

def collect_catastrophes_data():
    all_catastrophes = asyncio.run(get_gdacs_info())
    for catastrophe_entry in all_catastrophes:
        save_catastrophe(catastrophe_entry)
    print('data collected...\n#########################################################################\n\n')
