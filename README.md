# Engineering Project Management Agents

This project consists of a Python-based backend service and a Streamlit frontend.

## Setup and Running the Application

To run this application, you need to install both the system and Python dependencies and then start the backend and frontend servers.

### 1. Install System Dependencies

This application requires certain system-level libraries. Install them by running:

```bash
sudo apt-get update && sudo apt-get install -y $(cat packages.txt)
```

### 2. Install Python Dependencies

The frontend and backend have separate Python dependencies. Install them both:

```bash
pip install -r frontend/requirements.txt
pip install -r backend/requirements.txt
```

### 3. Run the Backend Server

The frontend requires the backend server to be running. To start the backend, run the following command in your terminal:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
```

This will start the server on `http://localhost:8000`.

### 4. Run the Frontend Application

Once the backend server is running, you can start the Streamlit frontend. Open a **new terminal** and run:

```bash
streamlit run frontend/app.py
```
