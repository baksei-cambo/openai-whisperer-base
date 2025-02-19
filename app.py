import whisper
import torch
import uuid
import os
import hashlib
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor

# Flask App
app = Flask(__name__)

# Use a ThreadPoolExecutor to manage background tasks
executor = ThreadPoolExecutor(max_workers=4)

# Dictionary to store job statuses & hash results
job_statuses = {}  # Stores {job_id: {"status": "...", "text": "..."}}
hash_results = {}  # Stores {file_hash: job_id}

# Select device (CUDA if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Model Cache Directory
MODEL_CACHE_DIR = "/app/model_cache"
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

# Load Whisper model once & cache it
print("Loading Whisper model...")
model = whisper.load_model("base", device=device, download_root=MODEL_CACHE_DIR)
print("Model loaded and cached at:", MODEL_CACHE_DIR)


def compute_file_hash(file_path):
    """Compute SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()


def transcribe_audio(audio_path, file_hash, job_id):
    """Background function to transcribe audio"""
    try:
        print(f"Task started for job: {job_id}")
        job_statuses[job_id] = {"status": "processing", "text": ""}

        # Verify if file exists before transcribing
        if not os.path.exists(audio_path):
            print(f"File not found: {audio_path}")
            job_statuses[job_id] = {"status": "error", "text": "File not found."}
            return

        print(f"Transcribing audio: {audio_path}")
        
        # Force FP32 to avoid FP16 warning
        result = model.transcribe(audio_path, fp16=False)
        transcribed_text = result["text"]

        print(f"Transcription completed for job: {job_id}")

        # Store the transcription result using the file hash
        hash_results[file_hash] = job_id
        job_statuses[job_id] = {"status": "completed", "text": transcribed_text}

    except Exception as e:
        print(f"Error in job {job_id}: {str(e)}")
        job_statuses[job_id] = {"status": "error", "text": str(e)}


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Endpoint to receive an audio file and process it asynchronously."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # Save the uploaded file temporarily
    audio_file = request.files["file"]
    temp_path = f"/tmp/{uuid.uuid4()}-{audio_file.filename}"
    audio_file.save(temp_path)

    # Compute the file hash
    file_hash = compute_file_hash(temp_path)

    # Check if this file has already been transcribed
    if file_hash in hash_results:
        existing_job_id = hash_results[file_hash]
        print(f"File with hash {file_hash} already transcribed. Returning existing job_id: {existing_job_id}")
        return jsonify({"job_id": existing_job_id, "status": job_statuses[existing_job_id]["status"], "text": job_statuses[existing_job_id]["text"]})

    # Generate a unique job ID
    job_id = str(uuid.uuid4())

    # Store initial job status
    job_statuses[job_id] = {"status": "queued", "text": ""}
    hash_results[file_hash] = job_id  # Link file hash to job ID

    # Enqueue the transcription task
    executor.submit(transcribe_audio, temp_path, file_hash, job_id)

    return jsonify({"job_id": job_id, "status": "queued", "status_url": f"/status/{job_id}"})


@app.route("/status/<job_id>", methods=["GET"])
def check_status(job_id):
    """Check the status of a transcription job."""
    if job_id not in job_statuses:
        return jsonify({"job_id": job_id, "status": "not found", "text": ""}), 404

    return jsonify({"job_id": job_id, "status": job_statuses[job_id]["status"], "text": job_statuses[job_id]["text"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
