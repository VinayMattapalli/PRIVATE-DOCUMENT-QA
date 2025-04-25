# Use slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential cmake git curl ffmpeg libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install piper-tts CLI + voice model
RUN pip install piper-tts \
    && mkdir -p app/models/tts \
    && curl -L -o app/models/tts/en_US-danny-low.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US-danny-low.onnx \
    && curl -L -o app/models/tts/en_US-danny-low.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US-danny-low.onnx.json

# Copy all app code
COPY . .

# Expose the Gradio port
EXPOSE 7860

# Launch the Gradio app on correct IP for Docker
CMD ["python", "ui.py"]
