import json
from datetime import datetime
import os

from flask import redirect, url_for

FOLDER_PATH = "static/user_data"

# -------------------------------------------------------------------
# 1. Create a translation dictionary for each language.
#    Feel free to refine or adjust the exact wording as needed.
# -------------------------------------------------------------------
language_mappings = {
    "en": {
        "welcome": "Greetings, noble soul! Behold, an AI wizard awaits to guide your diagnosis.",
        "welcome_back": "Ah, welcome back, {0}. The AI wizard stands ready to continue your quest.",
        "didnt_catch": "Prithee, I did not catch that. Couldst thou repeat?",
        "couldnt_understand": "Thy words confound me!",
        "consult_professional": "By your answers, thou mayst have {0}. Seek a learned physician for certain counsel.",
        "thank_you": "Thou hast my gratitude. Fare thee well!",
        "error_processing": "Alas, I struggle to parse thy words. Let us try anew.",
        "error_occurred": "Woe, an error has befallen us. Pray, try again later.",
        "gather_language": "en-US",
    },
    "de": {
        "welcome": "Seid gegrüßt, edle Seele! Ein KI-Zauberer steht bereit, eure Diagnose zu erhellen.",
        "welcome_back": "Willkommen zurück, {0}. Der KI-Zauberer ist bereit, eure Reise fortzusetzen.",
        "didnt_catch": "Verzeiht, ich habe euch nicht verstanden. Könntet ihr das wiederholen?",
        "couldnt_understand": "Eure Worte verwirren mich!",
        "consult_professional": "Euren Antworten nach könntet ihr {0} haben. Sucht einen kundigen Arzt auf.",
        "thank_you": "Ich danke euch. Lebt wohl!",
        "error_processing": "Leider kann ich eure Worte nicht deuten. Lasst es uns erneut versuchen.",
        "error_occurred": "Ein Fehler ist aufgetreten. Versucht es später erneut.",
        "gather_language": "de-DE",
    },
    "fr": {
        "welcome": "Salutations, âme noble! Un sorcier IA est prêt à guider votre diagnostic.",
        "welcome_back": "Soyez de retour, {0}. Le sorcier IA se tient prêt à poursuivre votre quête.",
        "didnt_catch": "Pardon, je n'ai pas compris. Pourriez-vous répéter?",
        "couldnt_understand": "Tes mots me troublent!",
        "consult_professional": "D'après tes réponses, tu pourrais avoir {0}. Consulte un médecin pour un avis sûr.",
        "thank_you": "Merci à toi. Adieu!",
        "error_processing": "Hélas, je peine à comprendre tes mots. Réessayons.",
        "error_occurred": "Un malheur est survenu. Réessaie plus tard.",
        "gather_language": "fr-FR",
    },
    "es": {
        "welcome": "Saludos, alma noble! Un mago IA aguarda para guiar tu diagnóstico.",
        "welcome_back": "Bienvenido de nuevo, {0}. El mago IA está listo para continuar tu búsqueda.",
        "didnt_catch": "Disculpa, no te he entendido. ¿Podrías repetirlo?",
        "couldnt_understand": "¡Tus palabras me confunden!",
        "consult_professional": "Según tus respuestas, podrías tener {0}. Consulta a un médico para un consejo certero.",
        "thank_you": "Te agradezco tu tiempo. ¡Adiós!",
        "error_processing": "Lamentablemente, no puedo entender tus palabras. Intentémoslo de nuevo.",
        "error_occurred": "Vaya, ha ocurrido un error. Por favor, inténtalo más tarde.",
        "gather_language": "es-ES",
    },
    "pt": {
        "welcome": "Saudações, alma nobre! Um mago de IA aguarda para guiar seu diagnóstico.",
        "welcome_back": "Bem-vindo de volta, {0}. O mago de IA está pronto para continuar sua jornada.",
        "didnt_catch": "Desculpe, não entendi. Poderia repetir?",
        "couldnt_understand": "Tuas palavras me confundem!",
        "consult_professional": "Pelas suas respostas, talvez você tenha {0}. Consulte um médico para uma opinião especializada.",
        "thank_you": "Agradeço o seu tempo. Adeus!",
        "error_processing": "Infelizmente, não consegui entender suas palavras. Vamos tentar novamente.",
        "error_occurred": "Ocorreu um erro. Tente novamente mais tarde.",
        "gather_language": "pt-PT",  # or pt-BR, depending on your preference
    },
    "it": {
        "welcome": "Saluti, nobile anima! Un mago IA è pronto a guidarti nella diagnosi.",
        "welcome_back": "Bentornato, {0}. Il mago IA è pronto a proseguire la tua missione.",
        "didnt_catch": "Scusa, non ho capito. Potresti ripetere?",
        "couldnt_understand": "Le tue parole mi confondono!",
        "consult_professional": "Dalle tue risposte, potresti avere {0}. Consulta un medico per un parere certo.",
        "thank_you": "Ti ringrazio. Addio!",
        "error_processing": "Sfortunatamente, non riesco a capire le tue parole. Riproviamo.",
        "error_occurred": "Si è verificato un errore. Riprova più tardi.",
        "gather_language": "it-IT",
    },
}

def get_translated_strings(lang="en"):
    """
    Return a dictionary of strings for the requested language.
    If lang is not found, default to English.
    """
    return language_mappings.get(lang, language_mappings["en"])

# -------------------------------------------------------------------
# 2. Example helper functions that use the translations.
#    Each function can take a language parameter (lang) and use it
#    to fetch the correct strings from the dictionary.
# -------------------------------------------------------------------

def load_traveler_history(scroll_number, lang="en"):
    texts = get_translated_strings(lang)
    print(texts["verifying"])  # "Verifying parchments... Please wait, kind soul."

    filename = f"{FOLDER_PATH}/user_history_{scroll_number}.json"
    if os.path.exists(filename):
        print(f"{texts['found']} {filename}")
        with open(filename, "r") as f:
            return json.load(f)
    else:
        print(texts["no_match"])
        print(texts["default_created"])

    # Return a default structure if no existing file
    return {
        "entries": [],
        "fname": "Nathan",
        "lname": "Zhao",
        "age": "30",
        "gender": "Other",
        "height": "170",
        "weight": "70",
        "current_call": [],
        "username": scroll_number,       # Could rename to "traveler_name" if desired
        "secret_word": "secret_word",    # Replaces "password"
        "scroll_number": scroll_number,  # Replaces "phone_number"
    }


def save_traveler_history(scroll_number, traveler_history, lang="en"):
    texts = get_translated_strings(lang)
    print(texts["saving"])  # "Saving the chronicle of your journey..."

    filename = f"{FOLDER_PATH}/user_history_{scroll_number}.json"
    with open(filename, "w") as f:
        json.dump(traveler_history, f, indent=2)

    print(texts["saved_success"])  # "The scroll is sealed with success."


def add_entry_to_history(traveler_history, new_info):
    # Just a helper function for appending new call data
    traveler_history["current_call"].extend(new_info)


def update_traveler_info(traveler_history, key, value):
    traveler_history[key] = value


def finalize_journey(traveler_history):
    # Append current call details to 'entries' if not empty
    if traveler_history["current_call"]:
        current_time = datetime.now().strftime("%m/%d/%Y %I:%M%p")
        traveler_history["entries"].append({current_time: traveler_history["current_call"]})
        traveler_history["current_call"] = []  # Clear after saving

    # Adjust if your route expects a different parameter name
    return redirect(
        url_for("medical_record", scroll_number=traveler_history["scroll_number"][1:])
    )
