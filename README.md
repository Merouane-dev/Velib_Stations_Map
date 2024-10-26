Documentation du Code
Ce script récupère les données en temps réel des stations Vélib à Paris, les stocke dans une base MongoDB, et les affiche sur une carte interactive via folium.

Dépendances
requests : Pour faire des requêtes HTTP vers l'API Vélib.
pymongo : Pour interagir avec MongoDB.
folium : Pour générer une carte interactive des stations Vélib.
webbrowser : Pour ouvrir automatiquement la carte générée dans le navigateur.
Fonctions
get_total_count()

Récupère le nombre total de stations depuis l'API Vélib.
Utilise une requête pour obtenir la valeur de total_count.
Retour : Un entier indiquant le nombre total de stations disponibles.
fetch_velib_data()

Récupère les données des stations Vélib par lot de 100 stations (pagination) depuis l'API.
Pour chaque lot de données, appelle update_database() pour les insérer ou les mettre à jour dans MongoDB.
Utilise un compteur d'offset pour récupérer toutes les données, quelles que soient les variations de nombre de stations.
update_database(data)

Prend un ensemble de données (lot de stations) et met à jour ou insère chaque station dans la collection MongoDB VelibApi.
Paramètres :
data : Liste de stations Vélib issues de l'API.
Met à jour chaque document en utilisant stationcode comme identifiant unique.
Appelle print_station_data() pour afficher les données dans la console après chaque mise à jour.
print_station_data()

Affiche les informations de chaque station Vélib dans la console.
Récupère tous les documents de la collection MongoDB et affiche les informations principales (nom, vélos disponibles, capacité, etc.).
display_map()

Génère une carte centrée sur Paris avec des marqueurs pour chaque station Vélib.
Pour chaque station, un marqueur est placé avec des informations sur le nom de la station.
Enregistre la carte sous le nom velib_map.html et l’ouvre automatiquement dans le navigateur.
run_scheduler()

Exécute fetch_velib_data() et display_map() à intervalle régulier (toutes les heures).
Utilise time.sleep(3600) pour attendre 1 heure entre chaque mise à jour.
Bloc principal

Si le script est exécuté en tant que programme principal, run_scheduler() est appelé, initiant le cycle de mise à jour et de génération de carte.
