# 🎭 Face Mesh & Emotion Tracking Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-v4.x-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange.svg)
![Flask](https://img.shields.io/badge/Flask-Web-lightgrey.svg)
![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-Control-yellow.svg)

An advanced, real-time Computer Vision web application that leverages MediaPipe and OpenCV to perform face landmark detection, blink counting, emotion estimation, and interactive cursor control via facial movements.

---

## 🚀 Key Features

* **Real-time 468-Point Face Tracking**: Uses MediaPipe's high-performance Face Mesh AI engine to precisely map facial structure.
* **Blink Detection**: Continuously monitors the Eye Aspect Ratio (EAR) across 12 specific anchor points mapping the eyes to accurately detect and count blinks.
* **Emotion Estimation Heuristics**: Calculates Mouth Aspect Ratio (MAR) and tracks corner lip displacement relative to the center lip to estimate expressions dynamically (Neutral, Happy, Surprised).
* **Nose Cursor Control (Beta)**: Translates your nose tip coordinates to corresponding system mouse movements. If enabled, blinking acts as a mouse click!
* **Glassmorphic Web Dashboard**: An incredibly aesthetic, fully responsive dark-mode UI that streams the webcam feed and reads live telemetry asynchronously.

---

## 🏗️ System Architecture & Data Flow

The system is broken into three main isolated components: The UI layer, the Server/Routing layer, and the AI/Inference Engine. 

```mermaid
graph TD
    classDef frontend fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef backend fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#fff;
    classDef engine fill:#7e22ce,stroke:#a855f7,stroke-width:2px,color:#fff;
    classDef hardware fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fff;

    subgraph Frontend [Web Dashboard - Glassmorphism UI]
        UI[index.html]:::frontend
        JS[main.js]:::frontend
        CSS[style.css]:::frontend
    end

    subgraph Backend [Flask Application Server]
        APP[app.py - Routing & Video HTTP]:::backend
    end

    subgraph Core Engine [Computer Vision & AI Inference]
        CV[OpenCV - Camera Buffer]:::engine
        MP[engine.py - MediaPipe AI Pipeline]:::engine
        CTRL[PyAutoGUI - System Control]:::engine
    end

    Camera[User Webcam]:::hardware -->|Capture Video| CV
    CV -->|Raw RGB Frame| APP
    APP -->|Process Frame| MP

    MP --> |1. Extract 468 Landmarks| LND[Face Landmarks Data]:::engine
    LND --> |2. Calculate Eye Aspect Ratio| BLNK[Blink Detection]:::engine
    LND --> |3. Calculate Mouth Matrix| EMT[Emotion Engine]:::engine
    LND --> |4. Nose Tip Positional Map| CTRL

    CTRL --> |Translate & Click| OS[Operating System Cursor]:::hardware
    
    MP --> |Annotated CV2 Frame & Dict Telemetry| APP
    
    APP --> |MJPEG Video Stream /video_feed| UI
    APP --> |JSON API Call /telemetry| JS
    
    JS --> |DOM Manipulation| UI
```

---

## 🔄 Sequence Workflow Diagram

This sequence illustrates a complete round-trip across the architecture for every frame visually processed and displayed.

```mermaid
sequenceDiagram
    participant U as User / Camera
    participant F as Frontend Browser
    participant B as Flask Backend
    participant E as Custom Engine

    U->>B: Start System
    B->>F: Serve Dashboard (HTML, CSS, JS)
    
    loop Real-time Frame Loop (30+ FPS)
        B->>E: Capture Frame
        E->>E: Inject RGB into MediaPipe Face Mesh
        E->>E: Process EAR, MAR, Landmarks
        
        opt If Cursor Control Turned On
            E->>U: Move OS Cursor via PyAutoGUI Native Call
            opt If Blink Detected
                E->>U: OS Mouse Click Trigger
            end
        end
        
        E-->>B: Return CV2 Graphic Frame & Telemetry Snapshot
        B-->>F: Stream Frame to `<img id="video-feed">` 
    end

    loop Asynchronous UI Updates (Every 250ms)
        F->>B: Fetch GET `/telemetry`
        B-->>F: Return active telemetry JSON format
        F->>F: Parse data & update dynamic dashboard widgets
    end
```

---

## 📁 System Project Structure

```text
c:/Face-Mesh/face-mesh-main/
│
├── app.py                 # Core routing layer, initialization, and CV video streaming
├── engine.py              # Specialized AI Engine - Math calculations & ML inference logic
├── mesh.py                # Base script for raw landmark detection 
├── requirements.txt       # Exhaustive list of python dependencies
│
├── static/
│   ├── main.js            # Frontend JavaScript for AJAX endpoints & Interactions
│   └── style.css          # Next-gen CSS styles (Dark mode + Glassmorphic components)
│
└── templates/
    └── index.html         # Jinja2 Layout & Application UI backbone
```

---

## ⚙️ Local Setup Instructions

Your environment requires a working Python installation (v3.10+ recommended). For the greatest stability, we isolate our project inside a local `venv`.

**1. Generate the Virtual Environment:**
```powershell
python -m venv venv
```

**2. Turn on Virtual Environment:**
```powershell
.\venv\Scripts\activate
```

**3. Install All Dependencies Tracked:**
```powershell
pip install -r requirements.txt
```

**4. Spin up the Analytics Server!**
```powershell
python app.py
```

Finally, visit [http://localhost:5000](http://localhost:5000) inside your web browser. 

---

### *A Note on Cursor Control Failsafes*
*When utilizing the experimental cursor control mechanism, moving your head tracks the mouse. Blinking clicks the mouse. If the cursor becomes erratic, PyAutoGUI FAILSAFE has intentionally been toggled off to avoid application snapping crashes at the physical border resolutions! Simply disable the button inside the web UI to regain immediate hardware mouse control.*
