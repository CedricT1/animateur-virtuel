# animateur.py

import sys
sys.path.append('data/configurations')

import requests
import random
import hashlib
import re
from datetime import date, datetime
from openai import OpenAI
from pydub import AudioSegment
import asyncio
import edge_tts
import config
import os
import json
import time
from bs4 import BeautifulSoup
from pathlib import Path

# Configuration IA
client = OpenAI(
    api_key=config.TOGETHER_API_KEY,
    base_url='https://api.together.xyz/v1',
)

# Variables globales pour les moteurs TTS
elevenlabs_client = None
google_client = None

# Import et configuration d'Elevenlabs seulement si nécessaire
if hasattr(config, 'TTS_ENGINE') and config.TTS_ENGINE.lower() == "elevenlabs":
    try:
        import elevenlabs
        if hasattr(config, 'ELEVENLABS_API_KEY'):
            elevenlabs_client = elevenlabs.ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
    except ImportError:
        print("ATTENTION: Module elevenlabs non trouvé. Edge TTS sera utilisé comme fallback.")
        config.TTS_ENGINE = "edge"

# Import et configuration de Google Cloud TTS seulement si nécessaire
if hasattr(config, 'TTS_ENGINE') and config.TTS_ENGINE.lower() == "google":
    try:
        from google.cloud import texttospeech
        import os
        
        if hasattr(config, 'GOOGLE_CREDENTIALS_FILE'):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GOOGLE_CREDENTIALS_FILE
            google_client = texttospeech.TextToSpeechClient()
    except ImportError:
        print("ATTENTION: Module google-cloud-texttospeech non trouvé. Edge TTS sera utilisé comme fallback.")
        config.TTS_ENGINE = "edge"
    except Exception as e:
        print(f"ATTENTION: Erreur lors de l'initialisation de Google Cloud TTS: {e}")
        print("Edge TTS sera utilisé comme fallback.")
        config.TTS_ENGINE = "edge"

# Date du jour
today = date.today()
formatted_date = today.strftime("%d.%m.%Y")

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
        - Reste naturel et chaleureux
        - Pas de formatage du texte en markdown ou html, tu es lus par un tts"""
    }
]

# Fonction pour simuler un dialogue avec un animateur de radio
def animateur_radio(prompt):
    """Fonction pour simuler un dialogue avec un animateur de radio."""
    # Ajoute le message utilisateur à l'historique
    historique_messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        messages=historique_messages,
        model=config.LLM_MODEL
    )

    retour1 = response.choices[0].message.content

    # Ajoute la réponse du modèle à l'historique
    historique_messages.append({"role": "assistant", "content": retour1})

    return retour1


# Fonction pour générer un fichier MP3 à partir d'un texte
async def _generate_mp3_from_text_edge(text):
    """Génère un fichier MP3 en utilisant Edge TTS."""
    communicate = edge_tts.Communicate(text, config.EDGE_VOICE, rate=config.EDGE_RATE, pitch=config.EDGE_PITCH)
    await communicate.save("temp.mp3")
    return "temp.mp3"

def _generate_mp3_from_text_elevenlabs(text):
    """Génère un fichier MP3 en utilisant Elevenlabs."""
    try:
        if elevenlabs_client is None:
            print("Client elevenlabs non disponible, utilisation de Edge TTS comme fallback")
            return asyncio.run(_generate_mp3_from_text_edge(text))
        
        # Génération de l'audio avec la nouvelle syntaxe
        audio_stream = elevenlabs_client.generate(
            text=text,
            voice=config.ELEVENLABS_VOICE_ID,
            model="eleven_multilingual_v2",
            voice_settings={
                "stability": getattr(config, 'ELEVENLABS_STABILITY', 0.5),
                "similarity_boost": getattr(config, 'ELEVENLABS_CLARITY', 0.75)
            }
        )
        
        # Conversion du stream en bytes et sauvegarde
        audio_bytes = b"".join(audio_stream)
        with open("temp.mp3", "wb") as f:
            f.write(audio_bytes)
        return "temp.mp3"
    except Exception as e:
        print(f"Erreur lors de la génération avec Elevenlabs: {e}")
        print("Utilisation de Edge TTS comme fallback")
        return asyncio.run(_generate_mp3_from_text_edge(text))

def _generate_mp3_from_text_google(text):
    """Génère un fichier MP3 en utilisant Google Cloud TTS."""
    try:
        if google_client is None:
            print("Client Google Cloud TTS non disponible, utilisation de Edge TTS comme fallback")
            return asyncio.run(_generate_mp3_from_text_edge(text))
        
        # Configuration de la synthèse
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Configuration de la voix
        voice = texttospeech.VoiceSelectionParams(
            language_code=config.GOOGLE_LANGUAGE_CODE,
            name=config.GOOGLE_VOICE
        )
        
        # Configuration audio
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=config.GOOGLE_SPEAKING_RATE,
            pitch=config.GOOGLE_PITCH
        )
        
        # Génération de l'audio
        response = google_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Sauvegarde du fichier audio
        with open("temp.mp3", "wb") as out:
            out.write(response.audio_content)
        
        return "temp.mp3"
    except Exception as e:
        print(f"Erreur lors de la génération avec Google Cloud TTS: {e}")
        print("Utilisation de Edge TTS comme fallback")
        return asyncio.run(_generate_mp3_from_text_edge(text))

def generate_mp3_from_text(text):
    """Fonction principale de génération TTS qui utilise le moteur configuré."""
    try:
        if config.TTS_ENGINE.lower() == "edge":
            return asyncio.run(_generate_mp3_from_text_edge(text))
        elif config.TTS_ENGINE.lower() == "elevenlabs":
            result = _generate_mp3_from_text_elevenlabs(text)
            if result is None:
                print("Échec de la génération avec Elevenlabs, utilisation de Edge TTS comme fallback")
                return asyncio.run(_generate_mp3_from_text_edge(text))
            return result
        elif config.TTS_ENGINE.lower() == "google":
            result = _generate_mp3_from_text_google(text)
            if result is None:
                print("Échec de la génération avec Google Cloud TTS, utilisation de Edge TTS comme fallback")
                return asyncio.run(_generate_mp3_from_text_edge(text))
            return result
        else:
            print(f"Moteur TTS non supporté: {config.TTS_ENGINE}, utilisation de Edge TTS comme fallback")
            return asyncio.run(_generate_mp3_from_text_edge(text))
    except Exception as e:
        print(f"Erreur lors de la génération TTS: {e}")
        print("Utilisation de Edge TTS comme fallback")
        return asyncio.run(_generate_mp3_from_text_edge(text))


def traiter_journal():
    """Génère et récupère le bulletin d'informations."""
    print("Génération du bulletin d'informations en cours...")
    
    # Envoi de la requête pour générer le bulletin
    try:
        response = requests.post("http://192.168.2.196:5000/api/generate_bulletin")
        data = response.json()
        
        if not data.get("success"):
            print(f"Erreur lors de la génération du bulletin: {data.get('error')}")
            print(f"Détails: {data.get('details')}")
            return None
            
        # Récupération du fichier audio
        audio_url = data["bulletin"]["audio_url"]
        print(f"Téléchargement du bulletin depuis {audio_url}")
        
        # Téléchargement du fichier audio
        audio_response = requests.get(audio_url)
        if audio_response.status_code == 200:
            with open("bulletin.mp3", "wb") as f:
                f.write(audio_response.content)
            return "bulletin.mp3"
        else:
            print(f"Erreur lors du téléchargement du bulletin: {audio_response.status_code}")
            return None
            
    except Exception as e:
        print(f"Erreur lors du traitement du bulletin: {e}")
        return None

def generate_unique_filename():
    """Génère un nom de fichier unique basé sur la date et l'heure"""
    now = datetime.now()
    return f"emission-{now.strftime('%d%m%y_%H%M')}.mp3"

def traiter_verset_du_jour():
    """Récupère le verset du jour depuis bible.com."""
    global formatted_date  # Déclarer l'utilisation de la variable globale
    try:
        # Récupération du verset
        response = requests.get('https://www.bible.com/fr/verse-of-the-day')
        html_content = response.text[:4000]

        # Extraction du verset
        prompt_extraction = (
            f"{html_content}\n"
            f"Ici dessus se trouve la page du verset du jour, je veux tu me l'extrait et que tu me retourne le verset suivis de sa référence, attention le verset sera lut par un speech to text donc tu ne commente rien du tout tu retourne uniquement le verset du jour et sa référence.\n"
        )

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un pasteur évangélique",
                },
                {
                    "role": "user",
                    "content": prompt_extraction,
                }
            ],
            model=config.LLM_MODEL
        )

        verset = response.choices[0].message.content
        print(f"Verset du jour : {verset}")
        return verset, formatted_date
        
    except Exception as e:
        print(f"Erreur lors de la récupération du verset du jour: {e}")
        return None, None

def main(script_filename):
    global formatted_date  # Déclarer l'utilisation de la variable globale
    
    # Authentification pour la partie podcast
    params = {
        "u": config.USERNAME,
        "p": config.PASSWORD,
        "v": "1.16.0",
        "c": "subsonic",
        "f": "json"
    }

    # Création du dossier emissions s'il n'existe pas
    os.makedirs("data/emissions", exist_ok=True)

    # Lecture du fichier script
    try:
        with open(f"data/configurations/{script_filename}", "r", encoding="utf-8") as file:
            script_content = file.read()
            # Remplace la balise {DATE} par la date du jour
            script_content = script_content.replace("{DATE}", formatted_date)
        
        # Définition du dictionnaire "chansons"
        chansons = {}
        
        # Création de l'émission audio
        emission = AudioSegment.empty()

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

            elif command[0] == "JOURNAL":
                print("Génération et insertion du journal...")
                bulletin_file = traiter_journal()
                if bulletin_file:
                    bulletin_segment = AudioSegment.from_file(bulletin_file)
                    emission += bulletin_segment
                    # Nettoyage du fichier temporaire
                    try:
                        os.remove(bulletin_file)
                    except Exception as e:
                        print(f"Erreur lors de la suppression du bulletin: {e}")
                else:
                    print("Impossible d'insérer le bulletin, on continue sans...")

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
                podcast_file = obtenir_podcasts(config.PODCAST_IDS[command[1].strip()], params)
                if podcast_file:
                    podcast_segment = AudioSegment.from_file(podcast_file)
                    emission += podcast_segment
            elif command[0] == "INTERLOCUTEUR":
                with open(command[1].strip(), 'r', encoding='utf-8') as fichier:
                    contenu = fichier.read()
                if config.TTS_ENGINE.lower() == "edge":
                    VOICE_backup = config.EDGE_VOICE
                    config.EDGE_VOICE = command[2].strip()
                    animateur = animateur_radio(contenu)
                    tts = generate_mp3_from_text(animateur)
                    emission += AudioSegment.from_mp3(tts)
                    config.EDGE_VOICE = VOICE_backup
                elif config.TTS_ENGINE.lower() == "elevenlabs":
                    VOICE_backup = config.ELEVENLABS_VOICE_ID
                    config.ELEVENLABS_VOICE_ID = command[2].strip()
                    animateur = animateur_radio(contenu)
                    tts = generate_mp3_from_text(animateur)
                    emission += AudioSegment.from_mp3(tts)
                    config.ELEVENLABS_VOICE_ID = VOICE_backup
                else:  # Google Cloud TTS
                    VOICE_backup = config.GOOGLE_VOICE
                    config.GOOGLE_VOICE = command[2].strip()
                    animateur = animateur_radio(contenu)
                    tts = generate_mp3_from_text(animateur)
                    emission += AudioSegment.from_mp3(tts)
                    config.GOOGLE_VOICE = VOICE_backup
            
            elif command[0] == "VERSET_DU_JOUR":
                print("Génération du verset du jour...")
                verset, formatted_date = traiter_verset_du_jour()
                if verset:
                    prompt_meditation = (
                        f"Voici le verset du jour du {formatted_date} : {verset}\n"
                        f"Maintenant Lit le verset du jour en annonçant la référence. Ensuite fais une courte méditation de doctrine évangélique sur ce verset."
                    )
                    animateur = animateur_radio(prompt_meditation)
                    print(f"REPONSE: {animateur}")
                    
                    # Génération du fichier audio
                    audio_file = generate_mp3_from_text(animateur)
                    
                    # Création du dossier versetjour s'il n'existe pas
                    os.makedirs("versetjour", exist_ok=True)
                    
                    # Sauvegarde avec un nom unique
                    now = datetime.now()
                    formatted_time = now.strftime("%Y%m%d%H%M")
                    output_path = f"versetjour/versetdu_{formatted_time}.mp3"
                    
                    # Copie directe du fichier audio
                    audio = AudioSegment.from_file(audio_file, format="mp3")
                    audio.export(output_path, format="mp3", bitrate="192k")
                    
                    if os.path.exists(output_path):
                        verset_audio = AudioSegment.from_mp3(output_path)
                        emission = emission + verset_audio
                    else:
                        print("Erreur: Impossible de générer le fichier audio du verset du jour")
                else:
                    print("Erreur: Impossible de récupérer le verset du jour")
        
        # Exportation du fichier final avec normalisation
        normalized_emission = emission.apply_gain(-20 - emission.dBFS)
        normalized_emission.export("output.mp3", format="mp3")
        print("Émission générée : output.mp3")

        # À la fin de la fonction main, avant de retourner
        output_filename = generate_unique_filename()
        output_path = os.path.join("data/emissions", output_filename)
        os.rename("output.mp3", output_path)
        print(f"Émission générée : {output_path}")
        return output_path

    except Exception as e:
        print(f"Erreur lors de la lecture du script: {e}")
        return None


# Fonction pour nettoyer les fichiers temporaires
def nettoyer_fichiers_temp():
    fichiers_temp = ["temp.mp3", "song.mp3", "podcast.mp3", "bulletin.mp3"]
    for fichier in fichiers_temp:
        try:
            if os.path.exists(fichier):
                os.remove(fichier)
        except Exception as e:
            print(f"Erreur lors du nettoyage de {fichier}: {e}")

if __name__ == "__main__":
    # Passer le nom de fichier du script d'émission comme argument
    main("script_emission.txt")

