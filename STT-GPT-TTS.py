import asyncio
import websockets
import json
import pyaudio
import wave
import webrtcvad
import collections
import audioop
import shutil
import os
import subprocess
import requests
import signal
import time
from gtts import gTTS

# Groq API Key
GROQ_API_KEY = "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"
VOICE_ID = "onwK4e9ZLuTAKqWW03F9"

# Audio and voice activity configuration
vad = webrtcvad.Vad(1)
FORMAT = pyaudio.paInt16
SAMPLE_RATE = 16000
CHUNK_DURATION_MS = 10
SILENCE_DURATION_MS = 700
CHANNELS = 1
THRESHOLD = 1200
LISTENING_BLOCKED = False
EXIT_FLAG = False
MAX_INACTIVITY_TIME = 10
LAST_SPEECH_TIME = time.time()
SPEAKING = False
AUDIO_STREAM = None
frames = collections.deque()

def is_installed(lib_name):
    """Check if a library is installed."""
    return shutil.which(lib_name) is not None

async def text_to_speech_input_streaming(voice_id, text_iterator):
    """Convert text to speech using gTTS."""
    for text in text_iterator:
        try:
            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en')  # Specify the language you prefer
            audio_file = "output.mp3"
            tts.save(audio_file)
            print(f"Audio saved as {audio_file}")

            # Play the audio (optional, based on your setup)
            os.system(f"start {audio_file}")  # For Windows, use 'start', for Linux use 'mpg123' or 'aplay'

        except Exception as e:
            print(f"Error generating speech: {e}")

async def chat_completion(query):
    """Retrieve text from Groq and pass it to the text-to-speech function."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",  # Updated model name
        "messages": [{"role": "user", "content": query}],
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            text_response = response_data["choices"][0]["message"]["content"]
            print(f"Chat Response: {text_response}")

            await text_to_speech_input_streaming(VOICE_ID, iter([text_response]))
        else:
            print(f"Failed to get chat completion: {response.status_code}")
            print(f"Error details: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Groq API: {e}")

def transcribe_audio(file_path):
    """Transcribe audio using Groq's Whisper API."""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": open(file_path, "rb")}
    data = {
        "model": "whisper-large-v3",
        "language": None,
        "prompt": None,
        "temperature": 0
    }
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.json().get("text", "No transcription available")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

async def process_recording():
    """Process recorded audio for transcription and chat completion."""
    global LISTENING_BLOCKED
    LISTENING_BLOCKED = True
    recorded_file = "recording.wav"

    transcript = transcribe_audio(recorded_file)
    if transcript:
        print(f"Transcript: {transcript}")
        await chat_completion(transcript)

    LISTENING_BLOCKED = False

async def main_loop():
    global LISTENING_BLOCKED, SPEAKING, AUDIO_STREAM, LAST_SPEECH_TIME
    silent_count = 0
    max_silent_iterations = 5

    audio = pyaudio.PyAudio()
    AUDIO_STREAM = audio.open(format=FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, input=True,
                              frames_per_buffer=int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000))

    num_silent_chunks_needed = int(SILENCE_DURATION_MS / CHUNK_DURATION_MS)
    num_silent_chunks = 0

    while True:
        if EXIT_FLAG:
            print("Exiting...")
            break

        if LISTENING_BLOCKED:
            print("Listening is blocked, waiting...")
            await asyncio.sleep(1)
            continue

        current_time = time.time()
        if current_time - LAST_SPEECH_TIME > MAX_INACTIVITY_TIME:
            print(f"No speech detected for {MAX_INACTIVITY_TIME} seconds. Exiting...")
            break

        print("Processing audio...")
        try:
            chunk = AUDIO_STREAM.read(int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000), exception_on_overflow=False)
            volume = audioop.rms(chunk, 2)
            is_speech = vad.is_speech(chunk, SAMPLE_RATE) and volume > THRESHOLD
        except Exception as e:
            print(f"Error processing audio: {e}")
            AUDIO_STREAM.close()
            AUDIO_STREAM = audio.open(format=FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, input=True,
                                      frames_per_buffer=int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000))
            await asyncio.sleep(0.05)
            continue

        if SPEAKING:
            frames.append(chunk)
            if not is_speech:
                num_silent_chunks += 1
                if num_silent_chunks > num_silent_chunks_needed:
                    print("Silence detected, saving recording...")
                    with wave.open("recording.wav", "wb") as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(audio.get_sample_size(FORMAT))
                        wf.setframerate(SAMPLE_RATE)
                        wf.writeframes(b''.join(frames))

                    await process_recording()
                    SPEAKING = False
                    frames.clear()
                    silent_count += 1
            else:
                num_silent_chunks = 0
        else:
            if is_speech:
                print("Speech detected, starting recording...")
                SPEAKING = True
                frames.append(chunk)
                num_silent_chunks = 0
                silent_count = 0
                LAST_SPEECH_TIME = time.time()

        if silent_count >= max_silent_iterations:
            print("Too many silent iterations. Exiting.")
            break

def signal_handler(sig, frame):
    """Handle KeyboardInterrupt and exit gracefully."""
    global EXIT_FLAG
    print('Exiting gracefully...')
    EXIT_FLAG = True

signal.signal(signal.SIGINT, signal_handler)

asyncio.run(main_loop())

