# Civic-Connect: Civic Problem & Pothole Reporting App

Civic-Connect is a web application built with Python and Streamlit that enables citizens to report civic problems (potholes, garbage, broken streetlights, water leakages, drainage blockages) in about a minute and track each complaint until resolution.

Many municipal reporting systems suffer from cumbersome forms, lack of duplicate detection, and opaque status updates. Civic-Connect provides an intuitive, guided workflow: attach a photo, verify location and timestamp, and submit.

> **Status:** Working prototype for civic demonstration and learning. Not yet linked directly to an automated municipal backend (see [Limitations](#limitations)).

---

## Features

- **Photo Upload & Privacy:** Supports JPG, PNG, WEBP (up to 10 MB). Uploads are resized and re-saved, automatically stripping sensitive EXIF data (including camera GPS tags).
- **Interactive Location Selection:**
  - Browser geolocation (GPS) via tap/click.
  - Interactive OpenStreetMap (Folium) pin dropping.
  - Manual coordinate entry.
  - Reverse geocoding to automatically resolve street addresses.
- **Duplicate Detection:** Checks for active issues of the same category within a 20-meter radius, allowing users to upvote existing issues instead of creating duplicates.
- **Categorization & Severity SLA:** Supports multiple municipal issue types with severity-based target resolution timeframes (SLA).
- **Interactive Map Overview:** Clustered visualization of issues colour-coded by status (Submitted, In Progress, Resolved).
- **Complaint Tracking & Timeline:** Lookup by reference ID (e.g., `CC-2026-123456`) with a 5-stage progress indicator.
- **Pre-filled Authority Email:** Automatically prepares a formatted email draft with complaint details for the responsible municipal authority.

---

## Tech Stack

| Component | Library / Service |
|---|---|
| Web Framework | [Streamlit](https://streamlit.io/) |
| Mapping & Visualization | [Folium](https://python-visualization.github.io/folium/), [streamlit-folium](https://github.com/randyzwitch/streamlit-folium) |
| Geolocation | [streamlit-geolocation](https://github.com/skrawcz/streamlit-geolocation) |
| Reverse Geocoding | [GeoPy](https://geopy.readthedocs.io/) (Nominatim / OpenStreetMap) |
| Image Processing | [Pillow](https://python-pillow.org/) |
| Environment & Config | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| Local Storage | JSON (`reports.json`) and local folder (`uploads/`) |

---

## Security & API Key Management

To keep secrets, API keys, and sensitive local data safe:
- **Environment Configuration:** All sensitive or environment-specific values are managed via a `.env` file.
- **Template Provided:** Refer to [`.env.example`](.env.example) for available environment variables (e.g., Nominatim User-Agent, Default Map Center, Authority Email, Max Upload Size).
- **Git Protection:** `.gitignore` is configured to prevent committing:
  - Secrets and environment files (`.env`, `*.key`, `*.pem`, `.streamlit/secrets.toml`).
  - Local database files containing citizen reports (`reports.json`).
  - User-uploaded photos (`uploads/*`).

To set up your local environment:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your custom values or API keys if needed
```

---

## Getting Started

### Prerequisites
- Python 3.10 or newer
- Internet access (for map tiles and address geocoding)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Mayank-Rathi-create/Road-watch.git
cd Road-watch

# 2. Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure environment variables
# Copy .env.example to .env and adjust if needed

# 5. Launch the application
streamlit run Civic-connect.py
# or
streamlit run app.py
```

The app will be accessible at `http://localhost:8501`.

---

## Project Structure

```text
Road-watch/
├── .env.example         # Template for environment variables and API keys
├── .gitignore            # Git exclusion rules for secrets, local reports, and uploads
├── app.py               # Application launcher entrypoint
├── Road_Watch.py        # Core Streamlit application logic
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── assets/              # Static media assets
│   └── background.png   # AI detection road background wallpaper
└── uploads/             # Directory for processed report photos (tracked via .gitkeep)
    └── .gitkeep
```

> **Note:** When reports are created locally, `reports.json` and images in `uploads/` will be generated. These are excluded from Git to protect user privacy.

---

## How to Use

1. **Report Issue:**
   - Go to the **Report** tab and upload a photo.
   - Set location using GPS, pin on the map, or coordinate entry.
   - Check the detected address and select category and severity.
   - Enter authority email (pre-filled if configured) and submit.
2. **Explore Map:**
   - Switch to the **Map** tab to view open, overdue, and resolved issues in your city.
3. **Track Status:**
   - Go to the **Track** tab and enter your reference ID (e.g., `CC-2026-123456`) to check real-time progress.

---

## Limitations

- **Simulated Municipal Backend:** Generates pre-formatted emails for local authorities; direct municipal API dispatch requires authority integration.
- **Local Storage:** Uses JSON file storage for lightweight single-node demonstration.
- **Nominatim Rate Limits:** Nominatim is a free community service limited to ~1 request/sec. For production, connect an API key via OpenCage, Mapbox, or LocationIQ.

---

## Future Scope

- Authority administrative portal and dashboard for status transitions.
- Automated ward-level routing based on municipal GeoJSON boundary maps.
- PostgreSQL / PostGIS database integration.
- SMS & WhatsApp status update notifications.
- Multi-language localization (Hindi, Kannada, etc.).

---

## Acknowledgements

- Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors.
- Geocoding powered by [Nominatim](https://nominatim.org/).

---

## Author

**Mayank Rathi**  
GitHub: [@Mayank-Rathi-create](https://github.com/Mayank-Rathi-create)
