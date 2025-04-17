from google.auth.transport.requests import Request
from sagemaker.s3 import S3Uploader, S3Downloader
from scipy.io.wavfile import write
from google.auth import default
from pydub import AudioSegment
from random import choice
from pathlib import Path

import numpy as np
import requests
import base64
import json
import os

if __name__ == '__main__':
    book_bucket = 's3://book-text-info'
    book_dir = Path('book-text-info')
    book_dir.mkdir(exist_ok=True)
    downloader = S3Downloader()
    downloader.download(book_bucket, book_dir)

    narr_bucket = 's3://sound-scribe-acessories/narrators.txt'
    downloader.download(narr_bucket, '.')

    files = list(book_dir.rglob('*-tagged.txt'))

    os.environ.setdefault('GOOGLE_CLOUD_PROJECT', "mlops-final-tts")
    for file in files:
        with open(file) as f:
            ssml = ''.join(f.readlines())

        with open('narrators.txt') as f:
            voices = f.readlines()

        name = choice(voices).strip()
        payload = {
            "input": {
                "ssml": ssml
            },
            "audioConfig": {
                "audioEncoding": "LINEAR16"
            },
            "voice": {
                "languageCode": "en-US",
                "name": name
            },
            "outputGcsUri": "gs://mlops-final-audio/output"
        }
        # Force token refresh
        credentials, project = default()
        credentials.refresh(Request())

        if credentials.token:
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "X-Goog-User-Project": "mlops-final-tts"
            }
            # print("Headers:", headers)
            response = requests.post('https://texttospeech.googleapis.com/v1beta1/projects/mlops-final-tts/locations/global:synthesizeLongAudio', headers=headers, json=payload)
            try:
                with open('audio.mp3', 'w') as f:
                    print(response.content)
                    f.write(response.json()['audioContent'])
                # Example: response.audio_content is the base64 string
                audio_bytes = base64.b64decode(response.json()["audioContent"])  # Decode first!

                # Manually add WAV header using parameters from your API response
                # Example: Sample rate=16000, channels=1 (mono)
                # Convert bytes to numpy array (16-bit PCM)
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                write(f"temp_{name}.wav", 24000, audio_array)  # Creates valid WAV file

                # Convert WAV to MP3
                AudioSegment.from_wav(f"temp_{name}.wav").export(f"output_{name}.mp3", format="mp3")

            except Exception as e:
                print(e.with_traceback())
        else:
            print("Authentication failed. Verify service account setup.")