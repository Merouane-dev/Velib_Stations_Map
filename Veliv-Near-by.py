import requests
import pymongo
import folium
import webbrowser
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import time

# Connexion à la base MongoDB
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Velib"]
mycol = mydb["VelibApi"]

# URL de base de l'API Vélib
base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"
limit = 100  # Limite de stations par requête


# Fonction pour récupérer le nombre total de stations depuis l'API
def get_total_count():
    response = requests.get(f"{base_url}?limit=1")
    response.raise_for_status()
    return response.json()["total_count"]


# Fonction pour récupérer les données depuis l'API avec pagination
def fetch_velib_data():
    offset = 0
    total_count = get_total_count()  # Récupération dynamique du nombre de stations

    while offset < total_count:
        url = f"{base_url}?limit={limit}&offset={offset}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json().get("records", [])
        update_database(data)  # Mettre à jour la base de données
        offset += limit


# Fonction pour mettre à jour la base MongoDB
def update_database(data):
    for station in data:
        fields = station['fields']
        station_data = {
            "stationcode": fields["stationcode"],
            "name": fields["name"],
            "lat": fields["coordonnees_geo"][0],
            "lon": fields["coordonnees_geo"][1],
            "capacity": fields["capacity"],
            "numbikesavailable": fields["numbikesavailable"],
            "numdocksavailable": fields["numdocksavailable"],
            "is_renting": fields["is_renting"],
            "is_returning": fields["is_returning"],
            "updated_at": datetime.now()
        }

        # Mettre à jour ou insérer la station dans MongoDB
        mycol.update_one(
            {"stationcode": fields["stationcode"]},  # Trouver la station par son code
            {"$set": station_data},  # Mettre à jour les champs
            upsert=True  # Ajouter si la station n'existe pas
        )


# Fonction pour afficher les stations dans un rayon de 500m
def display_nearby_stations(latitude, longitude):
    m = folium.Map(location=[latitude, longitude], tiles="OpenStreetMap", zoom_start=15)

    for station in mycol.find():
        station_coords = (station['lat'], station['lon'])
        user_coords = (latitude, longitude)

        # Calcul de la distance
        distance = geodesic(user_coords, station_coords).meters
        if distance <= 500:
            folium.Marker(
                station_coords,
                popup=f"<i>{station['name']}</i><br>{int(distance)} mètres",
                tooltip=f"<b>{station['name']}</b>"
            ).add_to(m)

    # Enregistrement et ouverture de la carte
    m.save("velib_nearby_map.html")
    webbrowser.open('velib_nearby_map.html')


# Fonction pour chercher l'adresse et afficher les stations proches
def search_and_display():
    address = address_entry.get()
    geolocator = Nominatim(user_agent="velib_locator")

    try:
        location = geolocator.geocode(address)
        if location:
            display_nearby_stations(location.latitude, location.longitude)
        else:
            messagebox.showinfo("Erreur", "Adresse non trouvée. Veuillez entrer une adresse valide.")
    except Exception as e:
        messagebox.showinfo("Erreur", f"Erreur lors de la géolocalisation: {e}")


# Interface graphique avec tkinter
root = tk.Tk()
root.title("Recherche de stations Vélib à proximité")

# Label et champ pour l'adresse
tk.Label(root, text="Entrez une adresse:").pack(pady=5)
address_entry = tk.Entry(root, width=50)
address_entry.pack(pady=5)

# Bouton pour lancer la recherche
search_button = tk.Button(root, text="Rechercher", command=search_and_display)
search_button.pack(pady=10)

# Lancer l'interface graphique
root.mainloop()
