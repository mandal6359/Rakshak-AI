# 🚆 Rakshak AI – Smart Railway Safety Command Center

## 📌 Introduction

Rakshak AI is an AI-powered Railway Safety and Surveillance Platform designed to improve passenger security, crowd management, and incident response inside railway stations.

The project was developed as part of a hackathon challenge where multiple problem statements were provided. Out of the available themes, we selected **Railway Safety & Smart Surveillance** because railway stations handle thousands of passengers daily, making real-time monitoring difficult for human operators.

Traditional CCTV systems rely on security personnel continuously watching multiple camera feeds, which often leads to delayed responses and missed incidents.

Rakshak AI acts as an intelligent monitoring assistant that automatically detects crowd gatherings, track intrusions, suspicious situations, and generates actionable alerts for security teams.

---

# 🎯 Problem Statement

Railway stations face several operational challenges:

* Large crowds during peak hours
* Track intrusion incidents
* Limited human monitoring capability
* Delayed response to emergencies
* Difficulty managing multiple CCTV streams simultaneously
* Lack of centralized AI-powered monitoring

Security operators are expected to monitor dozens of camera feeds continuously, which is practically impossible.

Rakshak AI addresses these issues using Computer Vision, Artificial Intelligence, Analytics, and Command Center Operations.

---

# 💡 Solution Overview

Rakshak AI transforms traditional CCTV infrastructure into an intelligent surveillance system capable of:

* Detecting people automatically
* Monitoring crowd density
* Detecting track intrusions
* Tracking passenger movement
* Generating alerts
* Logging incidents
* Visualizing station activity
* Assisting emergency response teams

The system converts raw CCTV footage into actionable intelligence.

# Rakshak AI Architecture Diagram


┌──────────────────────────────────────────────────────────┐
│                 RAKSHAK AI COMMAND CENTER                │
└──────────────────────────────────────────────────────────┘

                        CCTV NETWORK
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Camera 01   │ │ Camera 02   │ │ Camera N    │
│ Platform 1  │ │ Waiting Hall│ │ Track Area  │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
                RTSP VIDEO STREAMS
                       │
                       ▼

┌──────────────────────────────────────────────────────────┐
│                 AI PROCESSING ENGINE                     │
│                                                          │
│  YOLOv8 Person Detection                                │
│  Person Tracking                                        │
│  Crowd Gathering Detection                              │
│  Track Intrusion Detection                              │
│  Heatmap Generation                                     │
│  Risk Scoring Engine                                    │
│  Threat Severity Engine                                 │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼

┌──────────────────────────────────────────────────────────┐
│                 INCIDENT MANAGEMENT                      │
│                                                          │
│  Alert Generation                                       │
│  Evidence Snapshot Capture                              │
│  Incident Timeline                                      │
│  Dispatch Workflow                                      │
│  Emergency Response Actions                             │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼

┌──────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                       │
│                                                          │
│  SQLite / PostgreSQL                                    │
│                                                          │
│  Alerts Table                                           │
│  Dispatch Logs                                          │
│  Camera Registry                                        │
│  Zone Intelligence Data                                 │
│  Risk Analytics                                         │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼

┌──────────────────────────────────────────────────────────┐
│                ANALYTICS & VISUALIZATION                 │
│                                                          │
│  Crowd Heatmaps                                         │
│  Threat Statistics                                      │
│  Incident Analytics                                     │
│  Camera Performance Metrics                             │
│  Risk Dashboard                                         │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼

┌──────────────────────────────────────────────────────────┐
│              RAKSHAK AI COMMAND DASHBOARD               │
│                                                          │
│  Live CCTV Matrix                                       │
│  Threat Monitoring                                      │
│  Digital Twin Zone Intelligence                         │
│  Emergency Dispatch Center                              │
│  Incident Timeline                                      │
│  PDF Audit Reports                                      │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼

┌──────────────────────────────────────────────────────────┐
│                SECURITY OPERATIONS TEAM                  │
│                                                          │
│  Railway Protection Force (RPF)                         │
│  Station Security Officers                              │
│  Control Room Operators                                 │
└──────────────────────────────────────────────────────────┘

# Project Workflow

CCTV Camera
      ↓
RTSP Stream
      ↓
YOLOv8 Detection
      ↓
Crowd / Intrusion Analysis
      ↓
Threat Severity Engine
      ↓
Alert Generation
      ↓
Database Logging
      ↓
Heatmap Analytics
      ↓
Command Center Dashboard
      ↓
Security Team Response

---

# 🏗️ System Architecture

Railway CCTV Cameras
↓
Video Streams
↓
AI Processing Engine (YOLOv8)
↓
Threat Detection Layer
↓
Database Logging
↓
Analytics Engine
↓
Command Center Dashboard
↓
Security Personnel

---

# 🔥 Core Features

## 1. Person Detection

The system detects passengers in real-time using YOLOv8.

### Benefits

* Accurate passenger counting
* Real-time occupancy monitoring
* Foundation for advanced analytics

---

## 2. Person Tracking

Rakshak AI tracks detected passengers across frames.

### Benefits

* Movement monitoring
* Crowd behavior analysis
* Future support for watchlists

---

## 3. Crowd Gathering Detection

Detects abnormal crowd formations.

### Detection Logic

* Distance between people
* Group size thresholds
* Persistence over time

### Benefits

* Crowd management
* Congestion prevention
* Emergency planning

---

## 4. Track Intrusion Detection

Detects individuals entering restricted railway track zones.

### Benefits

* Passenger safety
* Accident prevention
* Immediate alert generation

---

## 5. Crowd Density Heatmap

Generates visual crowd density maps.

### Visualization

* Green → Low Density
* Yellow → Medium Density
* Red → High Density

### Benefits

* Station planning
* Peak-hour management
* Risk assessment

---

## 6. Multi-Camera Monitoring

Supports simultaneous monitoring of multiple CCTV feeds.

### Benefits

* Centralized monitoring
* Reduced operator workload
* Scalable architecture

---

## 7. Threat Severity Engine

Classifies incidents based on risk levels.

### Severity Levels

* LOW
* MEDIUM
* HIGH
* CRITICAL
* EMERGENCY

### Benefits

* Prioritized response
* Faster decision-making

---

## 8. Incident Logging System

All incidents are stored in SQLite.

### Stored Data

* Timestamp
* Camera ID
* Incident Type
* Severity
* People Count

---

## 9. Evidence Snapshot System

Automatically captures evidence during critical events.

### Benefits

* Audit trails
* Investigation support
* Incident documentation

---

## 10. Emergency Dispatch Workflow

Allows security operators to dispatch response teams.

### Dispatch Information

* Zone Name
* Team Assigned
* Dispatch Status
* Timestamp

---

## 11. Digital Twin Zone Intelligence

Railway zones are represented digitally.

### Example Zones

* Platform 1
* Platform 2
* Waiting Hall
* Ticket Counter
* Track Area

### Benefits

* Better situational awareness
* Location-specific monitoring

---

## 12. Analytics Dashboard

Provides real-time operational insights.

### Metrics

* Total Incidents
* Threat Levels
* Camera Status
* Passenger Counts
* Risk Scores

---

## 13. PDF Incident Reports

Generates downloadable audit reports.

### Report Contents

* Incident Summary
* Severity
* Evidence
* Camera Information
* Timeline

---

# 🖥️ Command Center Dashboard

The dashboard serves as the operational hub.

Features include:

* Live Camera Monitoring
* Threat Statistics
* Incident Timeline
* Dispatch Controls
* Zone Intelligence Matrix
* Crowd Heatmaps
* Evidence Viewer
* Risk Analytics

---

# 🛠️ Technology Stack

## AI & Computer Vision

* YOLOv8
* OpenCV
* NumPy

## Backend

* Python
* SQLite

## Frontend

* Streamlit

## Data Visualization

* Plotly
* Matplotlib

## Reporting

* ReportLab

---

# 📂 Project Structure

Rakshak-AI

backend/

* multi_camera_monitor.py
* heatmap.py
* dispatch.py
* cleanup.py

frontend/

* dashboard.py

database/

* alerts.db
* init_db.py

alerts/

* Evidence Snapshots

reports/

* PDF Reports

datasets/

* Videos
* Images

models/

* yolov8n.pt

README.md

---

# 🚀 Future Scope

Future versions of Rakshak AI can include:

* RTSP Live CCTV Integration
* Missing Person Search
* Face Recognition Watchlists
* Weapon Detection
* Abandoned Object Detection
* WhatsApp Alerts
* SMS Notifications
* Email Alerts
* Cloud Deployment
* Railway-Wide Command Center

---

# 🎯 Impact

Rakshak AI helps railway authorities:

* Improve passenger safety
* Reduce monitoring workload
* Detect threats early
* Improve emergency response
* Enable AI-assisted decision making

The project transforms passive CCTV infrastructure into an intelligent railway security ecosystem.

---

<!-- # 👨‍💻 Developed By

Piyush Prabhakar Mandal

B.Tech Computer Science (AI & ML)

Rakshak AI – Smart Railway Safety Command Center

"Protecting Passengers Through Intelligent Surveillance" -->

