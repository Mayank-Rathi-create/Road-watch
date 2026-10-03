# Road-watch
# RoadWatch: Pothole Reporting App

RoadWatch is a web app, built with Python and Streamlit, that lets citizens report potholes in about a minute and follow each complaint until it is resolved.

Many reporting tools have long forms, no duplicate detection and unclear status updates. RoadWatch uses a short guided flow: add a photo, confirm the location and time, and submit.

> **Status:** working prototype for learning and demonstration. It is not connected to any municipal system (see [Limitations](#limitations)).

## Features

- **Photo upload** with size and type checks (JPG, PNG, WEBP, max 10 MB). Photos are resized and re-saved, which removes EXIF data such as GPS coordinates.
- **Location input** by clicking an interactive OpenStreetMap map, using your current location (browser GPS), or typing coordinates.
- **Address lookup:** your current location is converted to a street address and filled in automatically. You can edit it.
- **Date and time** pre-filled, and not allowed to be in the future.
- **Validation:** submission is blocked until a photo, location and time are provided.
- **Duplicate detection:** if an open report exists within 20 m, you can upvote it instead of filing a new one.
- **Severity rating:** small, medium or dangerous.
- **Reports map** with pins coloured by status, plus summary counts and a recent-reports list.
- **Status tracker:** look up a complaint by reference number (for example `RW-2026-482113`) and see a five-stage timeline: Submitted, Acknowledged, Assigned, In progress, Resolved.
- **Email to the authority:** a pre-filled email with the complaint details opens in your mail app.

## Screenshots

Add your own screenshots here, for example:

```
![Report page](screenshots/report.png)
![Map page](screenshots/map.png)
![Track page](screenshots/track.png)
```

## Tech stack

| Purpose | Library |
|---|---|
| Web app framework | Streamlit |
| Maps | Folium, streamlit-folium (OpenStreetMap tiles) |
| Browser location | streamlit-geolocation |
| Address lookup | geopy (Nominatim) |
| Image processing | Pillow |
| Storage | JSON file and local folder |

## Getting started

**Requirements:** Python 3.10 or newer and an internet connection (for map tiles and address lookup).

```bash
# 1. Get the code
git clone <your-repo-url>
cd roadwatch

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run roadwatch_app.py
```

The app opens at `http://localhost:8501`. Use `localhost` or HTTPS, because browsers only allow location access on those.

`requirements.txt`:
```
streamlit
streamlit-folium
folium
pillow
geopy
streamlit-geolocation
```

## How to use

1. Open the **Report** tab and upload a photo of the pothole.
2. Tap the target icon to use your current location, or click the map to drop a pin.
3. Check the address, date, time and severity, and add notes if you like.
4. Optionally enter the authority's complaint email address, then press **Submit report**.
5. Save the reference number shown, and use the **Track** tab to follow progress.

## Project structure

```
roadwatch/
├── roadwatch_app.py     # the whole application
├── requirements.txt     # dependencies
├── reports.json         # created on first submission (saved reports)
├── uploads/             # created on first submission (processed photos)
└── README.md
```

To reset the demo data, delete `reports.json` and the `uploads/` folder.

## Limitations

- **No real municipal backend.** Nothing is sent automatically. You enter the authority's email, and the app opens a pre-filled email. Attach the photo before sending.
- **Simulated status updates.** The "advance status" button in the Track tab only simulates what a municipality would do.
- **Local storage only.** Data is kept in a JSON file on one machine. It does not suit many simultaneous users.
- **Location accuracy.** Laptops without GPS often locate by Wi-Fi or IP, so the pin can be off by hundreds of metres. The accuracy is shown, and the pin can be moved.
- **Address lookup limits.** Nominatim is a free service with a usage limit of about one request per second. Addresses in some areas may lack house numbers.
- **Time zone.** The "not in the future" check uses the clock of the machine running the app.

## Future scope

- Authority login and dashboard for updating statuses
- Automatic routing of complaints to the right ward using boundary data
- Database storage (PostgreSQL with PostGIS) and user accounts
- SMS and email notifications on status changes
- Kannada and Hindi language support
- Public dashboard of resolution times by ward
- Automated tests and deployment over HTTPS

## Acknowledgements

- Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors
- Address lookup by [Nominatim](https://nominatim.org/)

## Author

[Mayank Rathi]
