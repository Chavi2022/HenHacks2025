from dotenv import load_dotenv
import os
import requests
import boto3
from botocore.exceptions import NoCredentialsError
from botocore.config import Config
from convo_logic import generate_openai_response

load_dotenv()

S3_BUCKET_NAME = "jhubuckethophacks"
S3_OBJECT_NAME = "doctor1.mp3"
S3_REGION = "us-east-2"

language_voice_map = {
    "en": {"voice_id": "mCQMfsqGDT6IDkEKR20a", "language": "English"},
    "de": {"voice_id": "mCQMfsqGDT6IDkEKR20a", "language": "German"},
    "fr": {"voice_id": "mCQMfsqGDT6IDkEKR20a", "language": "French"},
    "es": {"voice_id": "mCQMfsqGDT6IDkEKR20a", "language": "Spanish"},
    "pt": {"voice_id": "mCQMfsqGDT6IDkEKR20a", "language": "Portuguese"},
    "it": {"voice_id": "mCQMfsqGDT6IDkEKR20a", "language": "Italian"},
}

# If you want, re-use the MEDIEVAL_MSG dictionary from user_history or define a simpler one:
MEDIEVAL_TTS_MSG = {
    "en": {
        "starting_tts": "Summoning the bard to recite thy text...",
        "translating": "Casting a translation spell for your words...",
        "uploading": "Uploading thy scroll to the cloud realm...",
        "credentials_missing": "Alas! We lack the necessary credentials for this magic.",
        "failed_upload": "Alack! The scroll could not be sealed.",
    },
    "de": {
        "starting_tts": "Beschwöre den Barden, um deinen Text vorzutragen...",
        "translating": "Wirken eines Übersetzungszaubers...",
        "uploading": "Lade deine Rolle in das Wolkenreich hoch...",
        "credentials_missing": "Oje! Uns fehlen die nötigen Berechtigungen für diese Magie.",
        "failed_upload": "Weh! Die Rolle konnte nicht versiegelt werden.",
    },
    # ... add fr, es, pt, it similarly ...
}

my_config = Config(region_name="us-east-2", signature_version="s3v4")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    config=my_config,
)

def translate_text(text, target_language):
    """
    Translates the given text to the target language using OpenAI's GPT model.
    """
    prompt = f"Translate the following text to {target_language}:\n\n{text}\n\nTranslation:"
    translated_text = generate_openai_response(prompt)
    return translated_text.strip()

def text_to_speech(text, language="en"):
    msg = MEDIEVAL_TTS_MSG.get(language, MEDIEVAL_TTS_MSG["en"])
    print(msg["starting_tts"])

    if language != "en":
        print(msg["translating"])
        text = translate_text(text, language_voice_map.get(language)["language"])
        # Possibly re-apply medieval style to the translated text

    CHUNK_SIZE = 1024
    voice_info = language_voice_map.get(language)
    voice_id = voice_info["voice_id"] if voice_info else None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.getenv("ELEVEN_API_KEY"),
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.8},
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200 or response.headers.get("Content-Type") != "audio/mpeg":
        print("Failed to retrieve valid audio data.")
        print(f"Response text: {response.text}")
        return None

    binary_audio_data = b""
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            binary_audio_data += chunk

    try:
        print(msg["uploading"])
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_OBJECT_NAME,
            Body=binary_audio_data,
            ContentType="audio/mpeg",
        )
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": S3_OBJECT_NAME},
            ExpiresIn=3600,
        )
        return presigned_url
    except NoCredentialsError:
        print(msg["credentials_missing"])
    except Exception as e:
        print(f"{msg['failed_upload']} Error: {e}")

    return None
