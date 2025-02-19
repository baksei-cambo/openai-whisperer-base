# Use Python base image
FROM python:3.10-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    ln -s /usr/bin/ffmpeg /usr/local/bin/ffmpeg

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel --root-user-action=ignore

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --root-user-action=ignore

# Install OpenAI Whisper & Flask
RUN pip install --no-cache-dir openai-whisper flask --root-user-action=ignore

# Create a non-root user
RUN groupadd -r whispergroup && useradd -m -r -g whispergroup whisperuser

# Create directories and set permissions for non-root user
RUN mkdir -p /app/model_cache /app/data /tmp && \
    chown -R whisperuser:whispergroup /app /tmp /app/model_cache /app/data

# Switch to non-root user
USER whisperuser

# Create model cache directory & pre-load Whisper model
RUN python -c "import whisper; whisper.load_model('base', download_root='/app/model_cache')"

# Copy project files
COPY . .

# Expose API port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
