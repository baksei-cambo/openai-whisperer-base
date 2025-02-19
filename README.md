# 🎙️ Whisper Transcription API 🚀

A lightweight **speech-to-text transcription API** powered by **OpenAI's Whisper model**.  
Supports **asynchronous transcription**, **file caching (SHA256 hash)** to avoid duplicate processing, and **runs with Docker** for easy deployment.

---

## 🚀 Features

✅ **Fast & Efficient**: Uses `multiprocessing` for async transcriptions.  
✅ **Avoids Reprocessing**: Caches transcriptions based on file hash (SHA256).  
✅ **Simple API**: Upload an audio file, get a `job_id`, and check transcription status.  
✅ **Docker Support**: Easily deploy with `docker-compose`.  
✅ **CPU & GPU Support**: Uses CUDA if available, otherwise defaults to CPU.

---

## 📦 Installation & Setup

### 🔹 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/whisper-api.git
cd whisper-api
```
