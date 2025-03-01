import json
from datetime import datetime
import os

from flask import redirect, url_for

FOLDER_PATH = "static/user_data"

# -------------------------------------------------------------------
# A dictionary for your medieval-themed messages in multiple languages.
# Adjust or refine the phrasing to your preference.
# -------------------------------------------------------------------
MEDIEVAL_MSG = {
    "en": {
        "verifying": "Verifying parchments... Please wait, kind soul.",
        "writ_no_match": "The writ doth not match the records. Try again, good traveler.",
        "scroll_number_label": "Scroll Number",
        "secret_word_label": "Secret Word",
        "saving": "Saving the chronicle of your journey...",
        "saved_success": "The scroll is sealed with success.",
    },
    "de": {
        "verifying": "Überprüfe Pergamente... Bitte warte, edle Seele.",
        "writ_no_match": "Die Schriftrolle stimmt nicht mit den Aufzeichnungen überein. Versuche es erneut, edler Reisender.",
        "scroll_number_label": "Schriftrollen-Nummer",
        "secret_word_label": "Geheimes Wort",
        "saving": "Speichere die Chronik deiner Reise...",
        "saved_success": "Die Schriftrolle wurde erfolgreich versiegelt.",
    },
    "fr": {
        "verifying": "Vérification des parchemins... Patientez, noble âme.",
        "writ_no_match": "Le parchemin ne correspond pas aux registres. Réessayez, cher voyageur.",
        "scroll_number_label": "Numéro du Parchemin",
        "secret_word_label": "Mot Secret",
        "saving": "Enregistrement de la chronique de votre voyage...",
        "saved_success": "Le parchemin a été scellé avec succès.",
    },
    "es": {
        "verifying": "Verificando pergaminos... Por favor, espera, alma noble.",
        "writ_no_match": "El pergamino no coincide con los registros. Inténtalo de nuevo, buen viajero.",
        "scroll_number_label": "Número del Pergamino",
        "secret_word_label": "Palabra Secreta",
        "saving": "Guardando la crónica de tu viaje...",
        "saved_success": "El pergamino ha sido sellado con éxito.",
    },
    "pt": {
        "verifying": "Verificando pergaminhos... Por favor, aguarde, alma nobre.",
        "writ_no_match": "O pergaminho não corresponde aos registros. Tente novamente, bom viajante.",
        "scroll_number_label": "Número do Pergaminho",
        "secret_word_label": "Palavra Secreta",
        "saving": "Salvando a crônica da sua jornada...",
        "saved_success": "O pergaminho foi selado com sucesso.",
    },
    "it": {
        "verifying": "Verifica dei pergamene... Per favore, attendi, anima gentile.",
        "writ_no_match": "La pergamena non corrisponde ai registri. Riprova, buon viaggiatore.",
        "scroll_number_label": "Numero della Pergamena",
        "secret_word_label": "Parola Segreta",
        "saving": "Salvataggio della cronaca del tuo viaggio...",
        "saved_success": "La pergamena è stata sigillata con successo.",
    },
}

def load_user_history(phone_number, lang="en"):
    """Load user history from a JSON file, showing 'medieval' style logs in the chosen language."""
    texts = MEDIEVAL_MSG.get(lang, MEDIEVAL_MSG["en"])

    print(texts["verifying"])  # e.g. "Verifying parchments... Please wait, kind soul."
    filename = f"{FOLDER_PATH}/user_history_{phone_number}.json"
    if os.path.exists(filename):
        print(f"filename: {filename}")
        with open(filename, "r") as f:
            return json.load(f)

    print(texts["writ_no_match"])  # e.g. "The writ doth not match the records..."
    # Return a default record if none exists
    return {
        "entries": [],
        "fname": "Luis",
        "lname": "Infantes",
        "age": "30",
        "gender": "Other",
        "height": "170",
        "weight": "70",
        "current_call": [],
        "username": phone_number,  # Still storing phone_number internally
        "password": "password",    # Original key, though displayed as 'secret_word' if desired
        "phone_number": phone_number,
    }


def save_user_history(phone_number, user_history, lang="en"):
    """Save user history to JSON, using medieval flavor messages."""
    texts = MEDIEVAL_MSG.get(lang, MEDIEVAL_MSG["en"])

    print(texts["saving"])  # e.g. "Saving the chronicle of your journey..."
    filename = f"{FOLDER_PATH}/user_history_{phone_number}.json"
    with open(filename, "w") as f:
        json.dump(user_history, f, indent=2)
    print(texts["saved_success"])  # e.g. "The scroll is sealed with success."


def add_entry_to_history(user_history, new_info):
    """Append new info (text, bullet points, etc.) to the 'current_call' list."""
    user_history["current_call"].extend(new_info)


def update_user_info(user_history, key, value):
    """Update a single field in the user's record, e.g. 'age', 'gender', etc."""
    user_history[key] = value


def finalize_call(user_history):
    """Move 'current_call' entries into the main 'entries' array with a timestamp, then redirect."""
    if user_history["current_call"]:
        current_time = datetime.now().strftime("%m/%d/%Y %I:%M%p")
        user_history["entries"].append({current_time: user_history["current_call"]})
        user_history["current_call"] = []  # Clear the current call info

    # Keep the existing redirect logic, but rename phone_number in user-facing text as needed
    return redirect(url_for("medical_record", phone_number=user_history["phone_number"][1:]))
