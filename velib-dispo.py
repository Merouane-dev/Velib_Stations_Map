import requests
import pymongo
import folium
import webbrowser
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

    print_station_data()  # Affiche les données dans la console


# Fonction pour afficher les données de la base dans la console
def print_station_data():
    entries = list(mycol.find())
    print("\nDonnées des stations Vélib dans la base de données :\n")
    for item in entries:
        print(f"Station: {item['name']} | Code: {item['stationcode']} | "
              f"Vélos disponibles: {item['numbikesavailable']} | "
              f"Places disponibles: {item['numdocksavailable']} | "
              f"Capacité: {item['capacity']} | "
              f"Location: ({item['lat']}, {item['lon']})\n")


# Fonction pour créer et afficher la carte
def display_map():
    entries = list(mycol.find())

    # Création de la carte centrée sur Paris
    m = folium.Map(location=[48.8566, 2.3522], tiles="OpenStreetMap", zoom_start=13)

    # Ajout de marqueurs pour chaque station
    for item in entries:
        folium.Marker(
            [item['lat'], item['lon']],
            popup=f"<i>{item['name']}</i>",
            tooltip=f"<b>{item['name']}</b>"
        ).add_to(m)

    # Enregistrement et ouverture de la carte
    m.save("velib_map.html")
    webbrowser.open('velib_map.html')


# Fonction pour exécuter le script toutes les heures
def run_scheduler():
    while True:
        fetch_velib_data()
        display_map()
        time.sleep(3600)  # Rafraîchit toutes les heures


# Lancer le script
if __name__ == "__main__":
    run_scheduler()
