# TripGenie: An Agentic AI-Based Autonomous Travel Planner

TripGenie is a state-of-the-art, production-ready multi-agent travel planning system powered by **LangGraph**, **FastAPI**, **MongoDB**, and **React (Vite + Tailwind CSS)**.

![TripGenie Architecture](https://img.shields.io/badge/Architecture-LangGraph%20Multi--Agent-emerald?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react)
![Tailwind](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC?style=for-the-badge&logo=tailwind-css)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248?style=for-the-badge&logo=mongodb)

---

## 🌟 Features

- **Autonomous Agentic Workflow**: Multi-agent network orchestrated by a Supervisor Agent utilizing LangGraph.
- **Natural Language & Form Planning**: Provide a simple prompt like *"4-day trip to Goa under ₹20,000 with beaches, nightlife, vegetarian food"* or use granular filter controls.
- **10 Specialized AI Agents**:
  1. **Supervisor Agent**: Coordinates workflow execution and routes tasks dynamically.
  2. **Planner Agent**: Formulates overall trip timeline and daily structure.
  3. **Destination Agent**: Highlights attractions, hidden gems, and optimal visiting hours.
  4. **Weather Agent**: Fetches weather forecasts for destination travel dates.
  5. **Transport Agent**: Recommends flights, trains, and intercity travel options.
  6. **Hotel Agent**: Selects lodging matching budget and luxury criteria.
  7. **Restaurant Agent**: Recommends dining options tailored to dietary needs (Vegetarian, Vegan, Non-Veg, Halal, etc.).
  8. **Budget Agent**: Itemizes financial breakdown and currency conversions.
  9. **Itinerary Agent**: Consolidates day-by-day hourly schedules.
  10. **Packing & Emergency Agent**: Generates custom gear lists, weather-specific wear, and emergency contacts.
  11. **Report Agent**: Formats complete travel package and exports PDF reports.
- **Real-Time Agent Thinking Stream**: Visualizes active sub-agents working step-by-step.
- **Interactive Map View**: Displays mapped pins for attractions, hotels, and dining spots.
- **JWT Authentication & Profile Management**: Complete user registration, secure password hashing, saved trips, and preference customization.
- **Dual LLM Engine Support**: Seamless switching between OpenAI (GPT-4/GPT-4.1) and Ollama (Local LLM) with built-in heuristic fallback mode for instant setup without API keys.
- **Dark Mode & Glassmorphic Design**: Modern Emerald/Deep Cyan aesthetic with smooth animations.

---

## 🏗️ Architecture & Multi-Agent Network

```
                               ┌─────────────────┐
                               │ Supervisor Agent│
                               └────────┬────────┘
                                        │
      ┌─────────────────────────────────┼─────────────────────────────────┐
      ▼                                 ▼                                 ▼
┌──────────────┐              ┌──────────────────┐               ┌────────────────┐
│Planner Agent │              │Destination Agent │               │ Weather Agent  │
└──────┬───────┘              └────────┬─────────┘               └───────┬────────┘
       │                               │                                 │
       ▼                               ▼                                 ▼
┌──────────────┐              ┌──────────────────┐               ┌────────────────┐
│ Hotel Agent  │              │ Transport Agent  │               │Restaurant Agent│
└──────┬───────┘              └────────┬─────────┘               └───────┬────────┘
       │                               │                                 │
       └───────────────────────────────┼─────────────────────────────────┘
                                       │
       ┌───────────────────────────────┴───────────────────────────────┐
       ▼                                                               ▼
┌──────────────┐                                               ┌──────────────┐
│ Budget Agent │                                               │ItineraryAgent│
└──────┬───────┘                                               └──────┬───────┘
       │                                                              │
       └───────────────────────────────┬──────────────────────────────┘
                                       │
                              ┌────────┴────────┐
                              │ Packing Agent   │
                              └────────┬────────┘
                                       │
                              ┌────────┴────────┐
                              │  Report Agent   │
                              └─────────────────┘
```

---

## ⚡ Quick Start

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- MongoDB (Optional, in-memory fallback included)

### 1. Backend Setup

```bash
cd server
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Start FastAPI dev server
python main.py
```
FastAPI server starts at `http://localhost:8000`. Swagger API docs accessible at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
cd client
npm install
npm run dev
```
Vite dev server starts at `http://localhost:5173`.

---

## 🐳 Docker Deployment

Run the entire full-stack application via Docker Compose:

```bash
docker-compose up --build
```

- **Frontend UI**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **MongoDB**: `localhost:27017`

---

## 📁 Directory Layout

```
TripGenie/
├── client/                 # React + Vite Frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components & agent stream visualizers
│   │   ├── context/        # Auth, Theme, and Trip contexts
│   │   ├── hooks/          # Custom hooks
│   │   ├── pages/          # 10 Application pages
│   │   ├── services/       # Axios API integrations
│   │   └── utils/          # Helpers & PDF generator
├── server/                 # FastAPI + LangGraph Backend
│   ├── app/
│   │   ├── agents/         # 11 Agent implementations
│   │   ├── api/            # REST API Routes
│   │   ├── config/         # Environment settings
│   │   ├── database/       # Motor MongoDB connection & seed scripts
│   │   ├── models/         # Pydantic & PyMongo models
│   │   ├── prompts/        # 10 Isolated Agent Prompts
│   │   ├── schemas/        # Request/Response validation schemas
│   │   ├── services/       # LangGraph Workflow & LLM Factory
│   │   └── tools/          # 8 Agent Tools (Weather, Maps, Hotels, etc.)
│   └── main.py             # Server entrypoint
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## 📄 License

MIT License © 2026 TripGenie AI Team.
