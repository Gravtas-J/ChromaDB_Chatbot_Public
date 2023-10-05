import requests
from elevenlabs import set_api_key
set_api_key("ea765153007ae088c23e83affa3cc8df")


CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/<voice-id>/stream"

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": "<xi-api-key>"
}

data = {
  "text": "Hi! My name is Bella, nice to meet you!",
  "model_id": "eleven_monolingual_v1",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}

response = requests.post(url, json=data, headers=headers, stream=True)

with open('output.mp3', 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            f.write(chunk)
