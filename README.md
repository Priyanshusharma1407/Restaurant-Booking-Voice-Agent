# Restaurant Booking Voice Agent — Full Stack Project
A voice-enabled restaurant booking system that allows users to create reservations using natural speech. The project includes a Python-based voice agent, a Node.js backend with MongoDB Atlas, and real-time weather integration.

## Features

### Voice Agent
- Captures and transcribes speech using Groq Whisper.
- Responds with text-to-speech using Groq TTS.
- Extracts booking details using LLM assistance.
- Guides the user through the booking process:
  - Name
  - Number of guests
  - Preferred date
  - Preferred time
  - Cuisine preference
  - Special requests
- Confirms the booking before submission.

### Backend (Node.js + Express)
- Stores booking details in MongoDB Atlas.
- Fetches real-time weather (temperature + description) using OpenWeather API.
- Suggests indoor/outdoor seating based on weather conditions.
- Provides REST API endpoints:
  - POST /api/bookings – Create a booking
  - GET /api/bookings – Get all bookings
  - GET /api/bookings/:id – Get a specific booking
  - DELETE /api/bookings/:id – Delete a booking

### Database
MongoDB Atlas stores:
- Customer name
- Guests count
- Date & time
- Cuisine preference
- Special requests
- Weather info
- Seating suggestion

## Project Structure

```
voice-agent/
│   agent.py
│   .env
│   venv/

backend/
│   server.js
│   package.json

│── controllers/
│      bookingcontroller.js

│── routes/
│      bookingRoutes.js

│── models/
│      Booking.js

│── utils/
       db.js
       weather.js
```

## Setup Instructions

### 1. Clone the repository

```
git clone <your-repo-url>
cd <project-folder>
```

## Backend Setup (Node + Express + MongoDB Atlas)

### 2. Install backend dependencies

```
cd backend
npm install
```

### 3. Create a `.env` file inside `backend/`

```
MONGO_URI=your_mongodb_atlas_connection_string
OPENWEATHER_API_KEY=your_openweather_api_key
PORT=5000
```

### 4. Start backend server

```
node server.js
```

Expected output:

```
Backend running on http://localhost:5000
Connected to MongoDB Atlas
```

## Voice Agent Setup (Python)

### 5. Install Python dependencies

```
cd voice-agent
pip install -r requirements.txt
```

### 6. Create `.env` inside `voice-agent/`

```
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

### 7. Run agent

```
python agent.py
```

## API Endpoints

### Create Booking
```
POST /api/bookings
```

### Get All Bookings
```
GET /api/bookings
```

### Get Booking by ID
```
GET /api/bookings/:id
```

### Delete Booking
```
DELETE /api/bookings/:id
```

## Technologies Used

### Frontend (Voice Agent)
- Python
- Groq Whisper (Speech-to-Text)
- Groq TTS (Text-to-Speech)
- LLM for detail extraction

### Backend
- Node.js
- Express.js
- MongoDB Atlas
- OpenWeather API

### Database
- MongoDB Atlas
- Mongoose ORM

## System Workflow

1. User speaks their booking request.
2. Voice agent transcribes and extracts necessary details.
3. Agent asks follow-up questions until all data is collected.
4. Agent presents a summary for confirmation.
5. On confirmation, backend fetches weather + saves booking.
6. MongoDB Atlas stores all details.
7. Agent receives weather-based seating recommendation and announces final confirmation.

## Deployment Options

Backend can be deployed on:
- Render
- Railway
- Vercel
- AWS EC2

Python agent runs locally.

## Submission Notes

This project demonstrates:
- Real-time speech recognition
- LLM-assisted data extraction
- Full-stack integration
- External API usage
- Cloud database operations
- Clean architecture
