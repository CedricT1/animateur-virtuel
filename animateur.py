# animateur.py

import requests
import random
import hashlib
import re
from datetime import date
from openai import OpenAI
from pydub import AudioSegment
import asyncio
import edge_tts
import config
import os

# Configuration IA
client = OpenAI(
    api_key=config.TOGETHER_API_KEY,
    base_url='https://api.together.xyz/v1',
)

# Date du jour
today = date.today()
formatted_date = today.strftime("%d.%m.%y")

# Fonction pour télécharger une chanson au hasard
def chansonhasard(track="hasard", telechargement=True):
    try:
        params = {
            "u": config.USERNAME,
            "p": config.PASSWORD,
            "v": "1.16.0",
            "c": "subsonic",
            "f": "json",
            "id": config.PLAYLIST_MUSIQUES_ID
        }
       
        response = requests.get(config.BASE_URL + "getPlaylist.view", params=params)

        if response.status_code == 200:
            data = response.json()
            playlist = data["subsonic-response"]["playlist"]
            if "entry" in playlist:
                songs = playlist["entry"]
                song = random.choice(songs)
            else:
                print("La playlist est vide.")
                return None
            print(f"Avant le if track vaux: {track}")
            if track.strip() != "hasard" :
                print(f"----------{track}-----------------")
                response2 = requests.get(config.BASE_URL + f"getSong?id={track.strip()}", params=params)
                data2 = response2.json()
                song = data2["subsonic-response"]["song"]
            else:
                print(f"##########{track}#############")

            song_info = {
                "title": song["title"],
                "artist": song["artist"],
                "album": song["album"],
                "id":  song["id"],
                "file_path": "song.mp3"
            }
            if telechargement:
                params["id"] = song["id"]
                response = requests.get(config.BASE_URL + "stream.view", params=params, stream=True)
                
                if response.status_code == 200:
                    with open("song.mp3", "wb") as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                else:
                    raise Exception(f"Erreur de téléchargement: {response.status_code}")

            return song_info
    except Exception as e:
        print(f"Erreur lors du téléchargement: {e}")
        return None


def obtenir_podcasts(podcast_id, params):
    # Rafraîchir tous les podcasts sur le serveur
    refresh_response = requests.get(f"{config.BASE_URL}refreshPodcasts.view", params=params)
    if refresh_response.status_code != 200:
        raise Exception("Erreur lors du rafraîchissement des podcasts")

    # Récupérer les podcasts spécifiques
    response = requests.get(f"{config.BASE_URL}getPodcasts.view", params={**params, "id": podcast_id})
    if response.status_code != 200:
        raise Exception("Erreur lors de la récupération des podcasts")

    podcast_data = response.json()

    # Vérifiez la structure du podcast_data pour extraire l'épisode et l'URL
    if "subsonic-response" in podcast_data:
        podcasts = podcast_data["subsonic-response"].get("podcasts", {}).get("channel", [])
        if podcasts:
            episodes = podcasts[0].get("episode", [])
            if episodes:
                last_episode = episodes[0]  # Obtenez le dernier épisode
                episode_id = last_episode['id']

                # Générer la signature pour la sécurité
                salt = ''.join(random.choice('0123456789abcdef') for i in range(6))
                token = hashlib.md5((params['p'] + salt).encode('utf-8')).hexdigest()

                # Construire l'URL de téléchargement
                download_url = f"{config.BASE_URL}download?id={episode_id}&v={params['v']}&u={params['u']}&s={salt}&t={token}&c=myapp"

                # Téléchargez le fichier audio
                audio_response = requests.get(download_url, stream=True)
                if audio_response.status_code == 200:
                    file_path = 'podcast.mp3'
                    with open(file_path, 'wb') as file:
                        for chunk in audio_response.iter_content(chunk_size=1024):
                            file.write(chunk)
                    print(f"Podcast téléchargé avec succès : {file_path}")
                    return file_path
                else:
                    raise Exception("Erreur lors du téléchargement de l'épisode du podcast")
            else:
                raise Exception("Aucun épisode disponible")
        else:
            raise Exception("Aucun podcast disponible")
    else:
        raise Exception("Erreur dans la réponse du serveur")


# Liste pour stocker l'historique des messages
historique_messages = [
    {
        "role": "system",
        "content": """Tu es un animateur de radio chrétienne, tu animes l'émission '1h de louange chez vous'.
        Consignes:
        - Sois clair et concis
        - Évite les tics de langage
        - Adapte ton ton à une radio chrétienne
        - Reste naturel et chaleureux"""
    }
]

# Fonction pour simuler un dialogue avec un animateur de radio
def animateur_radio(prompt):
    # Ajoute le message utilisateur à l'historique
    historique_messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        messages=historique_messages,
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    )

    retour1 = response.choices[0].message.content

    # Ajoute la réponse du modèle à l'historique
    historique_messages.append({"role": "assistant", "content": retour1})

    return retour1


# Fonction pour générer un fichier MP3 à partir d'un texte
async def _generate_mp3_from_text(text):
    communicate = edge_tts.Communicate(text, config.VOICE, rate=config.RATE, pitch=config.PITCH)
    await communicate.save("temp.mp3")
    return "temp.mp3"

def generate_mp3_from_text(text):
    return asyncio.run(_generate_mp3_from_text(text))


def main(script_filename):
    # Authentification pour la partie podcast
    auth_params = {"u": config.USERNAME, "p": config.PASSWORD, "c": "myapp", "v": "1.16.0", "f": "json"}
    # Définition du dictionnaire "chansons"
    chansons = {}
    
    # Création de l'émission audio
    emission = AudioSegment.empty()

    # Lecture du script et remplacement de la date
    with open(script_filename, 'r') as f:
        script_content = f.read()
        # Remplace toute date au format DD.MM.YY par la date du jour
        script_content = re.sub(r'\d{2}\.\d{2}\.\d{2}', formatted_date, script_content)
    
    # Traitement du script modifié ligne par ligne
    for lineprep in script_content.split('\n'):
        command = lineprep.strip().split(";")
        if command[0] == "PLAY_SONG":
            chanson = chansonhasard(command[2].strip(), False)
            if chanson:
                print(f"Joue la chanson : {chanson['title']}")
                chansons[command[1].strip()] = chanson 

    # Traitement final du script
    for line in script_content.split('\n'):
        command = line.strip().split(";")
        if command[0] == "START":
            print("Début de l'émission")
            print("En avant pour le jingle")
            song2 = AudioSegment.from_file("jingle.mp3")
            emission += song2

        elif command[0] == "INSERT":
            print("insert d'un fichier audio")
            song2 = AudioSegment.from_file(command[1].strip())
            emission += song2

        elif command[0] == "PLAY_SONG":
            song_id = command[1].strip()  # Récupérer directement l'ID de la chanson
            chanson_info = chansons.get(song_id)  # Obtenir les détails de la chanson
            if chanson_info:
                chanson = chansonhasard(chanson_info["id"])  # Passer l'ID à la fonction
                if chanson:
                    print(f"Joue la chanson : {chanson['title']}")
                    chansons[song_id] = chanson  # Mise à jour de la chanson jouée
                    song_segment = AudioSegment.from_file("song.mp3")
                    emission += song_segment
            else:
                print(f"Aucune chanson trouvée pour l'ID: {song_id}")
        elif command[0] == "NEXT_PROMPT":
            prompt = f"{command[1]}"
            for cle, valeur in chansons.items():
                if cle in prompt:  # Vérifie si la clé existe dans le prompt
                    # Créer une chaîne formatée avec les détails de la chanson
                    details_chanson = f"{valeur['title']} par {valeur['artist']} de l'album {valeur['album']}."
                    prompt = prompt.replace('[' + cle + ']', details_chanson, 1)
            print(f"PROMPT: {prompt}")
            animateur = animateur_radio(prompt)
            print(f"REPONSE: {animateur}")
            tts = generate_mp3_from_text(animateur)
            emission += AudioSegment.from_mp3(tts)
        elif command[0] == "ADD_PODCAST":
            podcast_file = obtenir_podcasts(config.PODCAST_IDS[command[1].strip()], auth_params)
            if podcast_file:
                podcast_segment = AudioSegment.from_file(podcast_file)
                emission += podcast_segment
        elif command[0] == "INTERLOCUTEUR":
            with open(command[1].strip(), 'r', encoding='utf-8') as fichier:
                contenu = fichier.read()
            VOICEbackup = config.VOICE
            config.VOICE = command[2].strip()
            animateur = animateur_radio(contenu)
            tts = generate_mp3_from_text(animateur)
            emission += AudioSegment.from_mp3(tts)
            config.VOICE = VOICEbackup
            
       
    # Exportation du fichier final
    emission.export("emission.mp3", format="mp3")
    print("Émission exportée sous le nom 'emission.mp3'.")


# Fonction pour nettoyer les fichiers temporaires
def nettoyer_fichiers_temp():
    fichiers_temp = ["temp.mp3", "song.mp3", "podcast.mp3"]
    for fichier in fichiers_temp:
        try:
            if os.path.exists(fichier):
                os.remove(fichier)
        except Exception as e:
            print(f"Erreur lors du nettoyage de {fichier}: {e}")

if __name__ == "__main__":
    # Passer le nom de fichier du script d'émission comme argument
    main("script_emission.txt")

