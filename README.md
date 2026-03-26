# 🎬 SnapVerse AI - Reel Generator

<div align="center">
  <em>Transform your photos into professional video reels with powerful automation.</em>

  **Features • Installation • Usage • API • Contributing**
</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [DevOps & Deployment](#-devops--deployment)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)

---

## 🌟 Overview

**SnapVerse AI** is a powerful Flask-based web application that allows users to create professional-quality video reels from photos and audio files — ideal for content creators, marketers, and social media enthusiasts.

### Why Choose SnapVerse AI?

✅ No Watermarks  
✅ Full HD Output (1080p)  
✅ Easy Drag & Drop Interface  
✅ 18+ Video Filters (Cinematic, Vintage, Noir, etc.)  
✅ Fast FFmpeg Processing  
✅ Docker Support  
✅ Export for Instagram, TikTok, YouTube, and more  

---

## ✨ Features

### 🎨 Core Features

#### 🖼️ Drag & Drop Upload
- Upload multiple images at once  
- Reorder easily  
- Supports JPG, JPEG, PNG  

#### 🎵 Audio Integration
- Add MP3 background music  
- Perfect sync with visuals  
- Up to 50MB audio  

#### ⚙️ Customization
- Adjustable duration (0.5–10 sec per image)  
- 18+ Video filters: Grayscale, Sepia, Cinematic, Vintage, Noir, Nashville, Vibrant, Warm, Cool, Dramatic, and more  
- Text overlay with custom positioning  
- Multiple aspect ratios  

#### 📐 Aspect Ratios
- **9:16** – Reels/Shorts  
- **16:9** – YouTube/Facebook  
- **1:1** – Instagram posts  

#### 💾 Gallery Management
- View, download, or delete reels  
- Metadata tracking (date, file size, settings)

#### 🎥 Bairan Effect (New)
- Upload a source video and optional slideshow images
- Automatic freeze-frame extraction and layered composition
- AI background removal using fal.ai (Bria)
- Output saved directly into your existing gallery

---

## 🎬 Video Specifications

| Feature | Specification |
|----------|----------------|
| Resolution | Full HD (1080p) |
| Frame Rate | 30 FPS |
| Video Codec | H.264 (MP4) |
| Audio Codec | AAC |
| Max Image Size | 10MB |
| Max Audio Size | 50MB |

---

## 📦 Prerequisites
- **Python 3.9+** (tested with 3.12)
- **FFmpeg**
  - Windows: Download from **[ffmpeg.org](https://ffmpeg.org/download.html)**
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
- **Docker** (optional, for containerized deployment)

---

## 🚀 Installation

### Standard Installation

```bash
# Clone repo
git clone https://github.com/h8815/AI-Reel-Generator-DevOps.git
cd AI-Reel-Generator-DevOps

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# OR
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Verify FFmpeg
ffmpeg -version

# Run the app
python main.py
```

### Docker Installation

```bash
# Build Docker image
docker build -t h8815/ai-reel-generator .

# Run container
docker run -p 5000:5000 -v $(pwd)/static:/app/static h8815/ai-reel-generator
```

App runs at: **http://localhost:5000**

---

## 🚀 DevOps & Deployment

### Quick Deploy with Docker Compose
```bash
# Start app with SonarQube & Trivy
docker-compose up -d
```

### Bairan Effect with Docker Compose
- `snapverse-ai` calls the internal `bairaneffect` service at `http://bairaneffect:3001/process`
- Set `FAL_KEY` in your `.env` file (or use the default in `docker-compose.yml`)
- Access the feature from the app navbar: `Bairan Effect`

### Kubernetes Deployment
```bash
# Deploy to K8s cluster
kubectl apply -f k8s/
```

### Infrastructure as Code (Terraform)
```bash
# Provision AWS infrastructure
cd terraform
terraform init
terraform apply
```

### CI/CD Pipeline
- ✅ Automated testing with pytest
- ✅ Security scanning (Trivy, SonarQube)
- ✅ Docker image build & push
- ✅ Kubernetes deployment
- ✅ Infrastructure provisioning

**📖 Full DevOps Documentation:**
- [DevOps Quick Start](DEVOPS_QUICKSTART.md)
- [Detailed DevOps Guide](DEVOPS.md)

---


## 📡 API Documentation

| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/` | Home page |
| GET | `/create` | Create reel page |
| POST | `/create` | Create a new reel |
| GET | `/gallery` | View created reels |
| POST | `/delete/<reel_name>` | Delete specific reel |
| GET | `/about` | About page |
| GET | `/help` | Help & FAQ page |

---

## 📁 Project Structure

```
Main-Project-SnapVerse-AI/
├── main.py                   # Main Flask application
├── generate_process.py       # Background processing script
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── pytest.ini                # Test configuration
├── templates/                # HTML templates
│   ├── index.html
│   ├── create.html
│   ├── gallery.html
│   ├── about.html
│   └── help.html
├── static/                   # Static files
│   ├── css/                  # Stylesheets
│   ├── reels/                # Generated reels (auto-created)
│   └── metadata/             # Reel metadata (auto-created)
├── tests/                    # Test files
│   └── test_app.py
├── user_uploads/             # Uploaded files (auto-created)
└── venv/                     # Virtual environment (not in repo)
```

---

## 🛠️ Technologies Used

### Backend
- Flask 3.1.0  
- FFmpeg (H.264 encoding)  
- Python 3.9+ (tested with 3.12)  
- Werkzeug 3.1.3  
- Gunicorn 23.0.0 (production server)

### Frontend
- HTML5, CSS3, JavaScript (ES6+)  
- Jinja2 Templates  

### Development & Testing
- pytest 8.4.2  
- black 25.9.0 (code formatter)  
- Docker (containerization)

### Core Libraries
- `subprocess`, `uuid`, `json`, `datetime`, `werkzeug.utils`

---

## 🤝 Contributing

### Steps
1. Fork the repo  
2. Create a branch  
3. Make & test changes  
4. Push branch  
5. Open a Pull Request  

### Guidelines
- Follow **PEP 8**  
- Use clear commit messages  
- Update docs for new features  
- Test thoroughly  

**Areas for Contribution:**  
🐛 Bug Fixes | ✨ New Filters | 📝 Docs | 🎨 UI/UX | 🧪 Tests | ⚡ Performance  

---

## 🙏 Acknowledgments

- **FFmpeg** – Video processing engine  
- **Flask** – Python web framework  
- **Werkzeug** – WSGI utilities  
- **Community** – Contributors & testers   

---

<div align="center">

Made with ❤️  
If this project helped you, please ⭐ star the repository!  

[Report Bug](#) • [Request Feature](#) • [Contribute](#)

</div>
