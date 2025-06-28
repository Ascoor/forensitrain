# ForensiTrain

ForensiTrain is a simple OSINT utility that performs live lookups on phone
numbers. It uses public APIs and command line tools such as Maigret to collect
metadata about a target number. Results include country, carrier information,
potential social media profiles and known breach exposure.

This project is provided **for educational and lawful OSINT use only**. Ensure
you comply with local laws and API terms of service before running queries.

## Local Development (No Docker)

### Backend

1. Create a Python virtual environment and activate it:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # on Windows use venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys.
4. Start the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
5. (Optional) Install Maigret globally for social profile lookups:
   ```bash
   pip install maigret
   ```

### Frontend

1. In a new terminal run:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

The React app will load at http://localhost:5173 and will query the API at
`http://localhost:8000/api`.

All phone lookups are logged to `logs/queries.log`.

### Unified Startup Script

To automatically set up both services without Docker run:

```bash
./forensitrain_start.sh
```

The script creates the backend virtual environment if needed, installs
dependencies, and launches the API and React frontend concurrently.

## Docker Deployment

1. Create a `.env` file in `backend/` with your API keys (see `.env.example`).
2. Build and start the stack:
   ```bash
   docker-compose up --build
   ```
   The backend will run on port `8000` and the frontend on ports `80`/`443`.
3. (Optional) Acquire TLS certificates using Let's Encrypt:
   ```bash
   ./deploy/certbot.sh yourdomain.com
   ```
   Certificates are stored in `./certbot/conf` and mounted into the Nginx container.

The frontend is served via Nginx which also proxies `/api/` requests to the FastAPI backend running with Gunicorn.

