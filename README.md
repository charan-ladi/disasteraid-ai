# DisasterAid AI

## 🌍 Offline AI Disaster Intelligence System

**DisasterAid AI** is an offline-first, CPU-powered AI application that transforms unstructured disaster reports into structured emergency records. It enables rescue teams and disaster management authorities to quickly understand, prioritize, and respond to emergencies without relying on cloud services or an internet connection.

Built for the **CPU-First Hackathon**, the application demonstrates that modern AI can run entirely on commodity hardware while remaining fast, reliable, and accessible.

---

# Problem Statement

During natural disasters such as floods, earthquakes, cyclones, landslides, and fires, emergency responders receive information in many different formats:

* Images
* Voice messages
* Videos
* PDF documents
* Text messages

These reports are often unstructured and difficult to process quickly. Rescue teams spend valuable time manually reading and organizing information before taking action.

Internet connectivity is also frequently unavailable during disasters, making cloud-based AI solutions impractical.

---

# Solution

DisasterAid AI processes disaster reports completely offline and converts them into structured emergency records.

Instead of reading hundreds of messages manually, responders receive organized information including:

* Disaster type
* Severity
* Number of affected people
* Medical emergencies
* Food and water requirements
* Location
* Resource requirements
* Priority score

This allows rescue teams to make faster and better-informed decisions.

---

# Key Features

### 📷 Image Processing

* Extract information from disaster photographs
* Detect visible damage indicators
* OCR for notices, banners, and official documents

### 🎤 Audio Processing

* Convert voice reports into text using offline speech recognition
* Extract emergency details automatically

### 🎥 Video Processing

* Process video frames
* Combine OCR and AI analysis
* Generate structured incident reports

### 📄 Document Processing

Supports:

* PDF reports
* Government notices
* Relief camp documents
* Situation reports

### 📝 Text Processing

Convert plain-language reports into structured emergency records.

Example:

**Input**

> Four people are trapped on the terrace near the old bridge. Water level is rising rapidly. One elderly person requires immediate medical assistance.

↓

**Output**

```json
{
  "disaster_type": "Flood",
  "people_trapped": 4,
  "elderly": 1,
  "medical_help": true,
  "severity": "Critical",
  "priority": "High"
}
```

---

# AI Pipeline

```
Image
Audio
Video
PDF
Text
      │
      ▼
Preprocessing
      │
      ▼
OCR + Speech-to-Text
      │
      ▼
Offline LLM
      │
      ▼
Structured JSON
      │
      ▼
SQLite Database
      │
      ▼
Dashboard & Search
```

---

# Technology Stack

| Component          | Technology                      |
| ------------------ | ------------------------------- |
| Frontend           | Streamlit                       |
| Backend            | Python                          |
| Database           | SQLite                          |
| OCR                | PaddleOCR                       |
| Speech Recognition | Whisper.cpp                     |
| Local LLM          | TinyLlama / Phi-3 Mini (Ollama) |
| Runtime            | CPU Only                        |
| Data Format        | JSON                            |
| Export             | CSV, JSON                       |

---

# Offline First

The application is designed to work completely offline.

✅ No internet connection required

✅ No cloud APIs

✅ CPU-only inference

✅ Local AI models

✅ Local database

---

# Project Structure

```
DisasterAid-AI/

├── app.py
├── database.py
├── requirements.txt
├── README.md
├── LICENSE
├── uploads/
├── exports/
├── assets/
├── models/
├── prompts/
├── utils/
│   ├── ocr.py
│   ├── speech.py
│   ├── video.py
│   ├── parser.py
│   └── database.py
└── data/
```

---

# Example Workflow

1. Launch the application.
2. Upload an image, video, audio recording, PDF, or text report.
3. The application processes the input locally.
4. AI extracts emergency information.
5. Structured data is stored in SQLite.
6. Rescue dashboard displays prioritized incidents.
7. Export reports as JSON or CSV.

---

# Example Structured Output

```json
{
  "incident_id": 1032,
  "disaster_type": "Flood",
  "severity": "Critical",
  "people_trapped": 4,
  "children": 2,
  "elderly": 1,
  "injuries": true,
  "medical_help": true,
  "food_needed": true,
  "water_needed": true,
  "location": "Old Bridge",
  "priority_score": 96,
  "status": "Immediate Rescue"
}
```

---

# Future Enhancements

* Multi-language disaster reports
* Offline map visualization
* Duplicate report detection
* Automatic incident clustering
* Damage estimation from satellite imagery
* Rescue route recommendations
* Local mesh-network synchronization
* SMS gateway integration
* Volunteer management dashboard

---

# Why DisasterAid AI?

* Fully offline operation
* Runs on CPU-only hardware
* Converts unstructured data into structured intelligence
* Open-source technologies
* Designed for disaster response scenarios
* Scalable for NGOs and government agencies
* Practical and impactful real-world application

---

# License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

---

# Team

Developed for the **CPU-First Hackathon**.

*"Turning disaster reports into actionable intelligence—offline, anywhere, on any CPU."*
