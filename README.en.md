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
- Social account scraping with avatar extraction
- Export reports as JSON or PDF
- Image intelligence with face, text and object detection
- Bilingual UI with dark mode
- Unified enrichment endpoint returning a confidence score

This project is provided **for legal and educational OSINT use only**. Ensure
you comply with local laws and API terms of service before running queries.

For a history of changes, see [CHANGELOG.md](CHANGELOG.md).

When running the FastAPI server directly, visiting `http://localhost:8000/` now
shows a short landing page that explains how to start the React frontend. The
actual user interface runs at `http://localhost:5173` when launched via
`npm run dev`.

## Requirements

- Python 3.10 (3.11 is also supported). `dlib`, a dependency of
  `face_recognition`, still lacks wheels for Python 3.12, so staying on 3.10
  avoids long build times.
- Node.js 18 or newer.

## Local Development

### Backend

1. Create a Python virtual environment and activate it:
   ```bash
   cd backend
   python3.10 -m venv venv
   source venv/bin/activate  # on Windows use venv\Scripts\activate
   ```
2. Install dependencies (includes `opencv-python-headless` for image analysis):
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
   npm install  # installs react-router-dom and react-icons
   npm run dev
   ```

The React app will load at http://localhost:5173. By default it queries the API
at `/api` by default. You can override this by creating a `.env` file
in `frontend/` containing `VITE_API_BASE=http://localhost:8000/api` for local development.

All phone lookups are logged to `logs/queries.log`.

### Unified Startup Script

To automatically set up both services run:

```bash
./forensitrain_start.sh
```

The script creates the backend virtual environment if needed, installs
dependencies, and launches the API and React frontend concurrently.

You can verify heavy dependencies by calling `/api/health`. The endpoint
returns a list of optional packages and whether they loaded successfully.

### Manual Testing

1. Run `./forensitrain_start.sh` and wait for both servers to start.
2. Open `http://localhost:5173` in your browser.
3. Enter a valid phone number such as `+12024561111` and submit.
4. Confirm general info, social accounts, and breach history populate.
   You can also POST to `/api/phone/enrich` for a merged response with a
   confidence score.
5. Check `logs/queries.log` for a new entry.
6. Try an invalid number to verify an error message is shown.

## Graph Visualization

`/api/phone/enrich` also returns a `graph` field describing relationships
between phones, emails and social accounts. You can visualize this using the
`GraphView` component.

```
import GraphView from './components/GraphView'

const sample = {
  nodes: [
    { id: '+12024561111', type: 'phone', label: 'Phone' },
    { id: 'user@example.com', type: 'email', label: 'Email' }
  ],
  links: [{ source: '+12024561111', target: 'user@example.com' }]
}

<GraphView graph={sample} />
```

When integrating with the API, pass `result.graph` from `enrichPhone` directly
into the component. It handles loading and error states automatically.

