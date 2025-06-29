# ForensiTrain

ForensiTrain is a simple OSINT utility that performs live lookups on phone
numbers. It uses public APIs and command line tools such as Maigret to collect
metadata about a target number. Results include country, carrier information,
potential social media profiles and known breach exposure.

-## Key Features

- Phone number parsing with `phonenumbers`
- Carrier and line type lookup using only `phonenumbers`
- Social profile discovery using Maigret
- Optional Sherlock lookup for more profiles
- Recursive intelligence lookups that reuse discovered emails and usernames
- Breach checks using public `scylla.sh` and `dehashed` datasets
- Export reports as JSON or PDF
- Image intelligence with face, text and object detection
- Bilingual UI with dark mode
- Unified enrichment endpoint returning a confidence score

This project is provided **for educational and lawful OSINT use only**. Ensure
you comply with local laws and API terms of service before running queries.

For a history of changes, see [CHANGELOG.md](CHANGELOG.md).

When running the FastAPI server directly, visiting `http://localhost:8000/` now
shows a short landing page that explains how to start the React frontend. The
actual user interface runs at `http://localhost:5173` when launched via
`npm run dev`.

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
3. Start the API:
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

The React app will load at http://localhost:5173. By default it queries the API
at `http://localhost:8000/api`. You can override this by creating a `.env`
file in `frontend/` containing `VITE_API_BASE=http://yourhost:8000/api`.

All phone lookups are logged to `logs/queries.log`.

### Unified Startup Script

To automatically set up both services without Docker run:

```bash
./forensitrain_start.sh
```

The script creates the backend virtual environment if needed, installs
dependencies, and launches the API and React frontend concurrently.

### Manual Testing

1. Run `./forensitrain_start.sh` and wait for both servers to start.
2. Open `http://localhost:5173` in your browser.
3. Enter a valid phone number such as `+12024561111` and submit.
4. Confirm general info, social accounts, and breach history populate.
   You can also POST to `/api/phone/enrich` for a merged response with a
   confidence score.
5. Check `logs/queries.log` for a new entry.
6. Try an invalid number to verify an error message is shown.

## Docker Deployment

1. Build and start the stack:
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

