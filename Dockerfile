# Use Python base image
FROM python:3.10-bullseye

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y ffmpeg \
    && ln -s /usr/bin/ffmpeg /usr/local/bin/ffmpeg \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 \
    && pip install --no-cache-dir openai-whisper flask

# Create model cache directory and download model
RUN mkdir -p /app/model_cache \
    && python -c "import whisper; whisper.load_model('base', download_root='/app/model_cache')"

# Copy project files into container
COPY . .

# Expose Flask API port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
