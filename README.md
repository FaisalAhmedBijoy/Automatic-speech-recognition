# Real-Time Speech Recognition with WebSockets

## Overview

This project is a FastAPI-based application for real-time speech recognition using WebSockets. It processes audio data streamed from the frontend, transcribes it using OpenAI's Whisper model, and sends the transcription back to the client in real time.

## Features

- Real-time speech recognition
- WebSocket-based communication
- Dockerized deployment for easy setup
- Configurable via environment variables
- CORS enabled for cross-origin requests

## Prerequisites

- Docker and Docker Compose
- Python 3.10+

```bash
pip install -r requirements.txt
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Build and Start the Application

```bash
docker compose -f docker-compose.yaml up --build
docker compose -f docker-compose.yaml up
```

This will start the application on port `6037`.

### 3. Access the Application

Open the frontend in your browser:

```plaintext
http://localhost:6037/speech/index
```

## Endpoints

### 1. Root Endpoint

**Endpoint:** `/speech`
**Method:** `GET`
**Description:** Returns a welcome message with the API version.
**Response:**

```json
{
  "message": "Welcome to the speech recognition API!"
}
```

### 2. Static Index Page

**Endpoint:** `/speech/index`
**Method:** `GET`
**Description:** Returns the static HTML page for the application.
**Response:**

- Status Code: `200`
- Content: HTML file (if exists) or error message.

### 3. WebSocket Endpoint

**Endpoint:** `/speech/audio`
**Description:** WebSocket endpoint for streaming audio data.

#### WebSocket Communication

- **Client to Server:**
  - Send binary audio data in chunks.
  - Send `"stop"` to clear the buffer and stop recording.
- **Server to Client:**
  - On successful transcription:
    ```json
    {
      "status": "success",
      "code": 200,
      "transcription": "<transcribed text>"
    }
    ```
  - On error:
    ```json
    {
      "status": "error",
      "code": 500,
      "message": "<error message>"
    }
    ```

## File Structure

```plaintext
.
├── app
│   ├── config
│   │   └── configurations.py
│   ├── routes
│   │   └── english_speech_recognition.py
|   |   └── english_speech_recognition.py
│   ├── static
│   │   └── index.html
│   ├── processing
│   │   └── audio_processing.py
│   └── main.py
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```

## WebSocket Frontend Integration

The `index.html` file uses JavaScript to interact with the WebSocket server. It captures audio from the user's microphone and streams it to the backend.

```javascript
const socket = new WebSocket("ws://localhost:6037/speech/audio");

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.status === "success") {
    transcriptionDisplay.textContent = data.transcription;
  } else {
    console.error("Error:", data.message);
  }
};
```

## Troubleshooting

### Common Issues

#### 1. `Unsupported upgrade request`

- **Cause:** Missing WebSocket library.
- **Solution:** Ensure `uvicorn[standard]` or `websockets` is installed in `requirements.txt`.

#### 2. `FileNotFoundError: index.html`

- **Cause:** Missing static file.
- **Solution:** Ensure `app/static/index.html` exists.

#### 3. CORS Errors

- **Solution:** Adjust `allow_origins` in `app/main.py`.

## License

This project is licensed under the MIT License.
