# Speech-to-Text and Text-to-Speech with Groq API

This project demonstrates the integration of speech recognition and text-to-speech using Python, the `gTTS` (Google Text-to-Speech) library, the `webrtcvad` library for voice activity detection, and the Groq API for AI-powered chat and transcription.

## Features

- **Speech Recognition**: Captures real-time audio from the microphone and transcribes it using Groq's Whisper API.
- **Text-to-Speech**: Converts the AI-generated text response into speech using Google Text-to-Speech (`gTTS`).
- **Real-time Interaction**: Continuously listens for voice input, processes speech, and provides a response.
- **Voice Activity Detection (VAD)**: Determines when speech is present or absent, and only records speech when active.
- **Groq API**: Uses Groq's chat completion and Whisper transcription APIs to interact with the user.

## Table of Contents

1. [Installation](#installation)
2. [Dependencies](#dependencies)
3. [Setup](#setup)
4. [Usage](#usage)
5. [How It Works](#how-it-works)
6. [License](#license)

## Installation

Follow these steps to set up the project:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/suprathickreddy/real-time-speech-assistant.git
    cd speech-to-text-text-to-speech
    ```

2. **Create a virtual environment** (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Dependencies

- `pyaudio`: Required for audio input and output handling.
- `wave`: For saving the recorded audio as `.wav` files.
- `requests`: For making HTTP requests to the Groq API.
- `gTTS`: For converting text to speech.
- `webrtcvad`: A library to detect speech presence.
- `asyncio`: For handling asynchronous tasks.
- `audioop`: For processing raw audio chunks.
- `shutil`: For handling file system operations.

### Install the necessary system libraries (if needed):

- **Windows**:
    - Install [PyAudio](https://pypi.org/project/PyAudio/) by following the official instructions for Windows.
- **Linux**:
    - Install system libraries:
        ```bash
        sudo apt-get install python3-pyaudio
        ```

## Setup

1. **Groq API Key**:
    - Obtain an API key from Groq (https://groq.com/).
    - Replace the `GROQ_API_KEY` in the code with your key.

2. **Voice Configuration**:
    - Set the `VOICE_ID` variable to the voice you want to use for text-to-speech (use Groq's API for this).

3. **Audio Configuration**:
    - Adjust the `SAMPLE_RATE`, `CHUNK_DURATION_MS`, and other settings to suit your audio setup.

4. **Run the Code**:
    Once you've installed the dependencies and configured the API keys, run the `main.py` script:
    ```bash
    python main.py
    ```

## Usage

- The program continuously listens for speech input using your microphone.
- Once speech is detected, it records the audio, sends it to Groq's Whisper API for transcription, and then uses Groq's chat API to generate a text response.
- The text response is converted to speech using `gTTS` and played back to the user.
- The program handles inactivity, speech detection, and grace period management, ensuring smooth interaction.

### Key Features
- **Voice Activity Detection (VAD)**: Automatically detects speech to start and stop recording.
- **Audio Transcription**: Converts recorded speech into text using Groq's Whisper API.
- **AI Chat**: Uses Groq's API to generate relevant responses based on the transcribed text.
- **Text-to-Speech (TTS)**: Converts the AI-generated text response into audio using `gTTS`.

## How It Works

1. **Audio Capture**: The program continuously captures audio from the microphone using `pyaudio`. 
2. **Speech Detection**: The `webrtcvad` library detects voice activity in the captured audio. If speech is detected, the program starts recording the audio.
3. **Transcription**: Once speech is detected and silence follows, the recorded audio is saved as a `.wav` file and sent to Groq's Whisper API for transcription.
4. **Chat Completion**: The transcribed text is sent to Groq’s chat completion API to generate an AI-powered response.
5. **Text-to-Speech**: The AI-generated text is passed to the `gTTS` library, which converts it into speech and plays it back to the user.

## Signal Handling

The program gracefully handles `SIGINT` (e.g., when pressing `Ctrl+C`), allowing for a smooth exit and cleanup of resources.

---

### Notes
- If you have any issues with dependencies like `pyaudio` on certain systems, check the [official PyAudio installation documentation](https://pypi.org/project/PyAudio/).
- Ensure that the microphone and audio devices are properly configured for recording and playback.
