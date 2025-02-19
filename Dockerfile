# Use Python base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Fix apt-get update issue by cleaning the lists first
RUN rm -rf /var/lib/apt/lists/* && mkdir -p /var/lib/apt/lists/partial

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install OpenAI Whisper & Flask
RUN pip install --no-cache-dir openai-whisper flask

# Create model cache directory & pre-load Whisper model
RUN mkdir -p /app/model_cache && \
    python -c "import whisper; whisper.load_model('base', download_root='/app/model_cache')"

# Copy project files
COPY . .

# Expose API port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
