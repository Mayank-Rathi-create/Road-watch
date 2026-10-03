"""
RoadWatch - pothole reporting app (Streamlit)

Install:  pip install streamlit streamlit-folium folium pillow geopy streamlit-geolocation
Run:      streamlit run roadwatch_app.py

Reports are saved locally in reports.json and photos in the uploads/ folder.
There is no real municipal backend: "sending" opens your email app with the
complaint pre-filled for the authority email you enter.
"""
import json
import math
import random
import urllib.parse
from datetime import datetime, date
from pathlib import Path

import folium
import streamlit as st
from geopy.geocoders import Nominatim
from PIL import Image, ImageOps
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

BASE = Path(__file__).parent
DATA = BASE / "reports.json"
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

STATUSES = ["Submitted", "Acknowledged", "Assigned", "In progress", "Resolved"]
CENTER = [12.9716, 77.5946]  # Bengaluru
DUP_RADIUS_M = 20
MAX_MB = 10

st.set_page_config(page_title="RoadWatch", page_icon="🕳️", layout="centered")


# ---------- storage ----------
def load_reports():
    try:
        return json.loads(DATA.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_reports(reports):
    DATA.write_text(json.dumps(reports, indent=2), encoding="utf-8")


def new_ref(reports):
    used = {r["ref"] for r in reports}
    while True:
        ref = f"RW-{date.today().year}-{random.randint(100000, 999999)}"
        if ref not in used:
            return ref


def save_photo(uploaded, ref):
    """Re-encode as a resized JPEG; this also strips EXIF (incl. GPS) data."""
    img = Image.open(uploaded)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((1000, 1000))
    path = UPLOADS / f"{ref}.jpg"
    img.save(path, "JPEG", quality=70)
    return str(path)


# ---------- helpers ----------
def distance_m(lat1, lng1, lat2, lng2):
    """Equirectangular approximation, accurate enough for tens of metres."""
    r = 6371000
    x = math.radians(lng2 - lng1) * math.cos(math.radians((lat1 + lat2) / 2))
    y = math.radians(lat2 - lat1)
    return math.hypot(x, y) * r


def find_duplicate(reports, lat, lng):
    for r in reports:
        if r["status"] < 4 and distance_m(lat, lng, r["lat"], r["lng"]) < DUP_RADIUS_M:
            return r
    return None


def status_color(status):
    return "green" if status >= 4 else "orange" if status >= 1 else "red"


def mailto_link(r, to):
    body = (
        f"Pothole complaint {r['ref']}\n"
        f"Location: {r['address'] or '(see coordinates)'}\n"
        f"Coordinates: {r['lat']:.5f}, {r['lng']:.5f}\n"
        f"Observed: {r['when']}\n"
        f"Severity: {r['severity']}\n"
        f"Notes: {r['notes'] or '-'}\n"
        f"Reporter contact: {r['contact'] or '-'}\n\n"
        "Please attach the photo before sending."
    )
    return (
        f"mailto:{urllib.parse.quote(to)}"
        f"?subject={urllib.parse.quote('Pothole complaint ' + r['ref'])}"
        f"&body={urllib.parse.quote(body)}"
    )


@st.cache_data(show_spinner=False, ttl=3600)
def _reverse(lat, lng):
    # Exceptions are not cached by Streamlit, so a failed lookup is retried next time.
    geo = Nominatim(user_agent="roadwatch-demo", timeout=8)
    loc = geo.reverse((round(lat, 5), round(lng, 5)), language="en")
    return loc.address if loc else ""


def reverse_geocode(lat, lng):
    """Coordinates -> street address via OpenStreetMap Nominatim (about 1 request/second max)."""
    try:
        return _reverse(lat, lng) or None
    except Exception:
        return None


def fill_address_from_pin():
    """Button callback: put the address of the current pin into the address box."""
    if ss.pin:
        addr = reverse_geocode(*ss.pin)
        if addr:
            ss[f"addr{ss.form_id}"] = addr
            ss.addr_msg = ("ok", addr)
        else:
            ss.addr_msg = ("warn", "Could not look up an address for this pin. Please type it in.")


# ---------- session state ----------
ss = st.session_state
ss.setdefault("pin", None)
ss.setdefault("form_id", 0)
ss.setdefault("last", None)  # last submitted (report, authority email)
ss.setdefault("gps_last", None)  # last GPS fix already applied
ss.setdefault("addr_msg", None)

reports = load_reports()

st.title("Road**Watch**")
tab_report, tab_map, tab_track = st.tabs(["Report", "Map", "Track"])


# ---------- REPORT ----------
with tab_report:
    if ss.last:
        r, to = ss.last
        st.success(f"Report submitted. Your reference number is **{r['ref']}**. Save it to track progress.")
        if to:
            st.markdown(f"[Email complaint to authority]({mailto_link(r, to)})")
            st.caption("Your email app opens with the details filled in. Attach the photo before sending.")
        else:
            st.info("No authority email was entered, so nothing has been sent.")
        if st.button("Report another pothole"):
            ss.last = None
            ss.pin = None
            ss.addr_msg = None
            ss.form_id += 1
            st.rerun()
    else:
        fid = ss.form_id
        st.subheader("Report a pothole")
        st.caption("Photo, location and time. About a minute.")

        photo = st.file_uploader(
            "1. Photo", type=["jpg", "jpeg", "png", "webp"], key=f"photo{fid}"
        )
        if photo:
            st.image(photo, width=260)

        st.markdown("**2. Location**")
        st.caption("Tap the target icon to use your current location. Your browser will ask for permission.")
        gps = streamlit_geolocation()
        g_lat, g_lng = gps.get("latitude"), gps.get("longitude")
        if g_lat is not None and g_lng is not None:
            fix = (round(g_lat, 5), round(g_lng, 5))
            if ss.gps_last != fix:  # new GPS reading: apply it once
                ss.gps_last = fix
                ss.pin = [g_lat, g_lng]
                addr = reverse_geocode(g_lat, g_lng)
                if addr:
                    ss[f"addr{fid}"] = addr
                    acc = gps.get("accuracy")
                    ss.addr_msg = ("ok", addr + (f"  (accuracy about {acc:.0f} m)" if acc else ""))
                else:
                    ss.addr_msg = ("warn", f"Location found ({g_lat:.5f}, {g_lng:.5f}) but no street address could be "
                                           "looked up. Please type it in.")
                st.rerun()

        address = st.text_input("Address or landmark", key=f"addr{fid}")
        if ss.addr_msg:
            kind, text = ss.addr_msg
            (st.success if kind == "ok" else st.warning)(
                f"Detected address: {text}" if kind == "ok" else text)
        if ss.pin:
            st.button("Fill address from the pin on the map", on_click=fill_address_from_pin)
        st.caption("Or click the map to drop a pin, or enter coordinates below.")

        m = folium.Map(location=ss.pin or CENTER, zoom_start=13 if not ss.pin else 16)
        for rep in reports:
            folium.CircleMarker(
                [rep["lat"], rep["lng"]], radius=5, color="gray", fill=True, fill_opacity=0.7
            ).add_to(m)
        if ss.pin:
            folium.Marker(ss.pin, icon=folium.Icon(color="blue")).add_to(m)
        out = st_folium(m, height=360, use_container_width=True,
                        returned_objects=["last_clicked"], key=f"pick{fid}")
        click = out.get("last_clicked") if out else None
        if click:
            new_pin = [click["lat"], click["lng"]]
            if ss.pin != new_pin:
                ss.pin = new_pin
                st.rerun()

        c1, c2 = st.columns(2)
        lat_in = c1.number_input("Latitude", value=float(ss.pin[0]) if ss.pin else 0.0,
                                 format="%.5f", key=f"lat{fid}_{ss.pin}")
        lng_in = c2.number_input("Longitude", value=float(ss.pin[1]) if ss.pin else 0.0,
                                 format="%.5f", key=f"lng{fid}_{ss.pin}")
        if (lat_in or lng_in) and ss.pin != [lat_in, lng_in] and -90 <= lat_in <= 90 and -180 <= lng_in <= 180:
            ss.pin = [lat_in, lng_in]
            st.rerun()

        # duplicate check
        if ss.pin:
            dup = find_duplicate(reports, *ss.pin)
            if dup:
                st.warning(
                    f"A report **{dup['ref']}** already exists within {DUP_RADIUS_M} m "
                    f"({dup.get('votes', 0)} upvotes)."
                )
                if st.button("Upvote it instead"):
                    for rep in reports:
                        if rep["ref"] == dup["ref"]:
                            rep["votes"] = rep.get("votes", 0) + 1
                    save_reports(reports)
                    st.success("Thanks, your upvote was added.")

        st.markdown("**3. Date and time**")
        d1, d2, d3 = st.columns([2, 2, 2])
        today = date.today()
        when_date = d1.date_input("Date", value=today, max_value=today, key=f"date{fid}")
        when_time = d2.time_input("Time", value=datetime.now().time().replace(second=0, microsecond=0),
                                  key=f"time{fid}")
        severity = d3.selectbox("Severity", ["Small", "Medium", "Dangerous"], index=1, key=f"sev{fid}")

        notes = st.text_area("Notes (optional)", key=f"notes{fid}", height=70)
        e1, e2 = st.columns(2)
        authority = e1.text_input("Authority email", placeholder="municipal complaint email", key=f"auth{fid}")
        contact = e2.text_input("Your email or phone (optional)", key=f"cont{fid}")

        if st.button("Submit report", type="primary", use_container_width=True):
            when = datetime.combine(when_date, when_time)
            errors = []
            loc_missing = ss.pin is None and not address.strip()
            if loc_missing:
                errors.append("Please provide the location and time before submitting your report.")
            if photo is None:
                errors.append("A photo is required.")
            elif photo.size > MAX_MB * 1024 * 1024:
                errors.append(f"Photo must be under {MAX_MB} MB.")
            if when > datetime.now():
                errors.append("Time cannot be in the future.")
            if authority and "@" not in authority:
                errors.append("Authority email looks invalid.")

            if errors:
                for e in dict.fromkeys(errors):
                    st.error(e)
            else:
                ref = new_ref(reports)
                try:
                    photo_path = save_photo(photo, ref)
                except Exception:
                    st.error("Could not read this image. Try a JPEG or PNG.")
                    st.stop()
                lat, lng = ss.pin if ss.pin else CENTER
                rec = {
                    "ref": ref, "lat": lat, "lng": lng, "pinned": ss.pin is not None,
                    "address": address.strip(), "when": when.strftime("%Y-%m-%d %H:%M"),
                    "severity": severity, "notes": notes.strip(), "contact": contact.strip(),
                    "photo": photo_path, "status": 0, "votes": 0,
                    "created": datetime.now().isoformat(timespec="seconds"),
                }
                reports.append(rec)
                save_reports(reports)
                ss.last = (rec, authority.strip())
                st.rerun()


# ---------- MAP ----------
with tab_map:
    st.subheader("Reports map")
    resolved = sum(1 for r in reports if r["status"] >= 4)
    a, b, c = st.columns(3)
    a.metric("Total", len(reports))
    b.metric("Open", len(reports) - resolved)
    c.metric("Resolved", resolved)

    big = folium.Map(location=CENTER, zoom_start=12)
    for r in reports:
        folium.Marker(
            [r["lat"], r["lng"]],
            popup=f"{r['ref']} · {STATUSES[r['status']]} · {r['severity']}",
            icon=folium.Icon(color=status_color(r["status"])),
        ).add_to(big)
    st_folium(big, height=420, use_container_width=True, returned_objects=[], key="bigmap")
    st.caption("Red: submitted. Orange: in progress. Green: resolved.")

    st.markdown("**Recent reports**")
    if not reports:
        st.write("No reports yet.")
    for r in reversed(reports[-8:]):
        col_img, col_txt = st.columns([1, 4])
        if Path(r["photo"]).exists():
            col_img.image(r["photo"], width=70)
        col_txt.markdown(
            f"**{r['ref']}** · {STATUSES[r['status']]}  \n"
            f"{r['address'] or 'Pinned location'} · {r['severity']} · {r.get('votes', 0)} upvotes"
        )


# ---------- TRACK ----------
with tab_track:
    st.subheader("Track a complaint")
    ref_in = st.text_input("Reference number", placeholder="RW-2026-123456").strip().upper()
    if ref_in:
        rep = next((r for r in reports if r["ref"] == ref_in), None)
        if rep is None:
            st.error("No report found with that reference on this machine.")
        else:
            st.markdown(f"### {rep['ref']} · {STATUSES[rep['status']]}")
            st.caption(f"{rep['address'] or 'Pinned location'} · {rep['severity']} · "
                       f"{rep.get('votes', 0)} upvotes · observed {rep['when']}")
            if Path(rep["photo"]).exists():
                st.image(rep["photo"], width=240)
            st.progress((rep["status"] + 1) / len(STATUSES))
            for i, s in enumerate(STATUSES):
                st.markdown(f"{'✅' if i <= rep['status'] else '⬜'} {s}")
            if rep["status"] < 4:
                if st.button("Demo: advance status"):
                    rep["status"] += 1
                    save_reports(reports)
                    st.rerun()
                st.caption("In a live system the municipality updates this. The button only simulates it.")

st.divider()
st.caption("Demo build: data is stored on this machine only.")