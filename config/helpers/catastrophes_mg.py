import asyncio
import aiohttp
from aio_georss_gdacs import GdacsFeed
from googletrans import Translator

translator = Translator()

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
                                catastrophe_info[k] = v
                            catastrophe[attr] = catastrophe_info
                        else:
                            translated_value = translator.translate(str(value), src='en', dest='fr').text
                            catastrophe[attr] = translated_value
                    catastrophes.append(catastrophe)
        return catastrophes

def is_location_in_madagascar(entry):
    lat, lon = entry.coordinates
    return -25 <= lat <= -12 and 43 <= lon <= 50

def collect_catastrophes_data():
    all_catastrophes = asyncio.run(get_gdacs_info())
    print(all_catastrophes)
