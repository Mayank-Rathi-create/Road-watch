"""
Civic-Connect - report municipal problems (Streamlit)

Citizens can report potholes, garbage, broken streetlights, drainage problems and
other civic issues. Each report gets a reference number and a target resolution time.

Install:  pip install -r requirements.txt
Run:      streamlit run app.py  (or: python -m streamlit run app.py / streamlit run Road_Watch.py)

Reports are saved locally in reports.json and photos in the uploads/ folder.
There is no real municipal backend: "sending" opens your email app with the
complaint pre-filled for the authority email you enter.

IMPORTANT: the resolution times in CATEGORIES below are placeholder targets chosen
for this demo. Replace them with the official service-level timelines of your
municipality before presenting them to users as real commitments.
"""
import base64
import json
import math
import os
import random
import urllib.parse
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

# Load environment configuration (.env) if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import folium
import streamlit as st
from geopy.geocoders import Nominatim
from PIL import Image, ImageOps
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

from municipal_directory import (
    find_nearest_municipality,
    search_authorities,
    MUNICIPAL_AUTHORITIES,
)


BASE = Path(__file__).parent
DATA = BASE / "reports.json"
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

STATUSES = ["Submitted", "Acknowledged", "Assigned", "In progress", "Resolved"]

# Environment-configurable settings (with safe defaults)
DEFAULT_LAT = float(os.getenv("DEFAULT_LATITUDE", "12.9716"))  # Bengaluru default
DEFAULT_LNG = float(os.getenv("DEFAULT_LONGITUDE", "77.5946"))
CENTER = [DEFAULT_LAT, DEFAULT_LNG]
DUP_RADIUS_M = int(os.getenv("DUP_RADIUS_M", "20"))
MAX_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
NOMINATIM_UA = os.getenv("NOMINATIM_USER_AGENT", "civic-connect-demo")
DEFAULT_AUTH_EMAIL = os.getenv("DEFAULT_AUTHORITY_EMAIL", "")

# Problem type -> target days to resolve a "Medium" severity report (EDIT THESE).
CATEGORIES = {
    "Pothole / road damage": 7,
    "Garbage / waste collection": 3,
    "Streetlight not working": 5,
    "Drainage / sewage blockage": 5,
    "Water supply / leakage": 3,
    "Fallen tree / branch": 2,
    "Footpath / public property damage": 14,
    "Other municipal issue": 14,
}
# Severity changes the target: dangerous problems get a shorter target.
SEV_FACTOR = {"Small": 1.5, "Medium": 1.0, "Dangerous": 0.5}
LEGACY_CATEGORY = "Pothole / road damage"  # reports saved before categories existed

st.set_page_config(page_title="Civic-Connect", page_icon="🏙️", layout="centered")


def get_local_now():
    """
    Returns the current local datetime, honoring APP_TIMEZONE or defaulting to Asia/Kolkata (IST).
    Returns a naive datetime for full compatibility with Streamlit date & time pickers.
    """
    tz_str = os.getenv("APP_TIMEZONE", "Asia/Kolkata")
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(tz_str)).replace(tzinfo=None)
    except Exception:
        pass

    if tz_str in ("Asia/Kolkata", "Asia/Calcutta", "IST", "Asia/Colombo", ""):
        ist = timezone(timedelta(hours=5, minutes=30))
        return datetime.now(ist).replace(tzinfo=None)

    return datetime.now()


def set_page_background():
    """Sets the provided rainy road AI detection image as the full-viewport app background."""
    bg_path = BASE / "assets" / "background.png"
    if not bg_path.exists():
        return
    try:
        with open(bg_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"], .stApp {{
                background-image: linear-gradient(rgba(14, 17, 23, 0.82), rgba(14, 17, 23, 0.88)),
                                  url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            [data-testid="stHeader"] {{
                background-color: transparent !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass


set_page_background()


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
    year = get_local_now().year
    while True:
        ref = f"CC-{year}-{random.randint(100000, 999999)}"
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


def cat_of(rep):
    return rep.get("category", LEGACY_CATEGORY)


def find_duplicate(reports, lat, lng, category):
    """An open report of the same type within DUP_RADIUS_M metres."""
    for r in reports:
        if (r["status"] < 4 and cat_of(r) == category
                and distance_m(lat, lng, r["lat"], r["lng"]) < DUP_RADIUS_M):
            return r
    return None


def status_color(status):
    return "green" if status >= 4 else "orange" if status >= 1 else "red"


# ----- target resolution time -----
def target_days(category, severity):
    base = CATEGORIES.get(category, CATEGORIES["Other municipal issue"])
    return max(1, math.ceil(base * SEV_FACTOR.get(severity, 1.0)))


def human_days(n):
    if n <= 14:
        return f"{n} day{'s' if n != 1 else ''}"
    return f"about {round(n / 7)} weeks"


def due_date(rep):
    if "due" in rep:
        return date.fromisoformat(rep["due"])
    try:
        created = datetime.fromisoformat(rep["created"]).date()
    except (KeyError, ValueError):
        created = get_local_now().date()
    return created + timedelta(days=target_days(cat_of(rep), rep.get("severity", "Medium")))


def days_left(rep):
    return (due_date(rep) - get_local_now().date()).days


def is_overdue(rep):
    return rep["status"] < 4 and days_left(rep) < 0


def deadline_text(rep):
    if rep["status"] >= 4:
        return "Resolved"
    d = days_left(rep)
    if d > 1:
        return f"{d} days left"
    if d == 1:
        return "1 day left"
    if d == 0:
        return "due today"
    return f"overdue by {-d} day{'s' if d != -1 else ''}"


def fmt_date(d):
    return d.strftime("%d %b %Y")


def format_when(val):
    """Format stored timestamp string into clean 12-hour format (e.g., 12/10/2026, 06:08 PM)."""
    if not val:
        return "-"
    if "AM" in val or "PM" in val:
        return val
    try:
        dt = datetime.strptime(val, "%Y-%m-%d %H:%M")
        return dt.strftime("%d/%m/%Y, %I:%M %p")
    except Exception:
        return val


def mailto_link(r, to):
    auth_name = r.get("authority_name") or "Municipal Authority"
    body = (
        f"To: The Grievance Officer / Municipal Commissioner,\n"
        f"{auth_name}\n\n"
        f"Subject: Civic Complaint regarding {cat_of(r)} (Ref: {r['ref']})\n\n"
        f"Respected Sir/Madam,\n\n"
        f"I wish to lodge a formal civic complaint regarding the following issue in your jurisdiction:\n\n"
        f"• Complaint Reference: {r['ref']}\n"
        f"• Problem Category: {cat_of(r)}\n"
        f"• Severity: {r.get('severity', 'Medium')}\n"
        f"• Location / Address: {r.get('address') or '(Coordinates provided below)'}\n"
        f"• GPS Coordinates: {r['lat']:.5f}, {r['lng']:.5f}\n"
        f"• Date & Time Observed: {format_when(r.get('when', ''))}\n"
        f"• Reporter Contact: {r.get('contact') or 'Anonymous / Not provided'}\n\n"
        f"Additional Description / Notes:\n"
        f"{r.get('notes') or 'None provided.'}\n\n"
        f"Expected Resolution SLA: within {human_days(r.get('target_days', 7))}\n\n"
        f"Please inspect and resolve this problem at the earliest.\n\n"
        f"[Note: Please attach the complaint photo before sending this email.]"
    )
    subject = f"[{r['ref']}] {cat_of(r)} - Complaint to {auth_name}"
    return (
        f"mailto:{urllib.parse.quote(to)}"
        f"?subject={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(body)}"
    )


@st.cache_data(show_spinner=False, ttl=3600)
def _reverse_full(lat, lng):
    # Exceptions are not cached by Streamlit, so a failed lookup is retried next time.
    try:
        geo = Nominatim(user_agent=NOMINATIM_UA, timeout=8)
        loc = geo.reverse((round(lat, 5), round(lng, 5)), language="en")
        if loc:
            raw_addr = getattr(loc, "raw", {}).get("address", {})
            return loc.address or "", raw_addr
    except Exception:
        pass
    return "", {}


def reverse_geocode(lat, lng):
    """Coordinates -> street address via OpenStreetMap Nominatim (about 1 request/second max)."""
    addr, _ = _reverse_full(lat, lng)
    return addr or None


def get_address_details(lat, lng):
    """Coordinates -> raw address dictionary for municipal identification."""
    _, raw = _reverse_full(lat, lng)
    return raw


def fill_address_from_pin():
    """Button callback: put the address and nearest municipality of current pin into the form."""
    if ss.pin:
        addr, raw_details = _reverse_full(*ss.pin)
        if addr:
            ss[f"addr{ss.form_id}"] = addr
            ss.addr_msg = ("ok", addr)
        else:
            ss.addr_msg = ("warn", "Could not look up an address for this pin. Please type it in.")
        auth = find_nearest_municipality(ss.pin[0], ss.pin[1], raw_details)
        ss.nearest_auth = auth
        ss[f"auth{ss.form_id}"] = auth["email"]
        ss.last_detected_pin = list(ss.pin)


# ---------- session state ----------
ss = st.session_state
ss.setdefault("pin", None)
ss.setdefault("form_id", 0)
ss.setdefault("last", None)  # last submitted (report, authority email)
ss.setdefault("gps_last", None)  # last GPS fix already applied
ss.setdefault("addr_msg", None)
ss.setdefault("nearest_auth", None)
ss.setdefault("last_detected_pin", None)

reports = load_reports()

st.title("Civic Connect")
tab_report, tab_map, tab_track = st.tabs(["Report", "Map", "Track"])


# ---------- REPORT ----------
with tab_report:
    if ss.last:
        r, to = ss.last
        st.success(f"Report submitted. Your reference number is **{r['ref']}**. Save it to track progress.")
        st.info(
            f"Expected resolution: within **{human_days(r['target_days'])}** "
            f"(target date {fmt_date(due_date(r))}). This is a target for this type of problem, "
            "not a guarantee."
        )
        if to:
            auth_disp = r.get("authority_name") or "Municipal Authority"
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 12px 16px; margin: 12px 0;">
                    <div style="font-weight: 600; color: #6ee7b7; font-size: 0.95rem;">🏛️ Targeted Authority: {auth_disp}</div>
                    <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 4px;">Destination email: <code>{to}</code></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(f"[✉️ Email complaint to {auth_disp}]({mailto_link(r, to)})")
            st.caption("Your email app opens with the formal complaint pre-filled for this municipal office. Attach the photo before sending.")
        else:
            st.info("No authority email was entered, so nothing has been sent.")
        if st.button("Report another problem."):
            ss.last = None
            ss.pin = None
            ss.addr_msg = None
            ss.nearest_auth = None
            ss.last_detected_pin = None
            ss.form_id += 1
            st.rerun()
    else:
        fid = ss.form_id
        st.subheader("Report a problem")
        st.caption("Potholes, garbage, streetlights, drainage and other civic issues. About a minute.")

        category = st.selectbox("1. What is the problem?", list(CATEGORIES), key=f"cat{fid}")

        photo = st.file_uploader(
            "2. Photo", type=["jpg", "jpeg", "png", "webp"], key=f"photo{fid}"
        )
        if photo:
            st.image(photo, width=260)

        st.markdown("**3. Location**")
        st.caption("Tap the target icon to use your current location. Your browser will ask for permission.")
        gps = streamlit_geolocation()
        g_lat, g_lng = gps.get("latitude"), gps.get("longitude")
        if g_lat is not None and g_lng is not None:
            fix = (round(g_lat, 5), round(g_lng, 5))
            if ss.gps_last != fix:  # new GPS reading: apply it once
                ss.gps_last = fix
                ss.pin = [g_lat, g_lng]
                addr, raw_details = _reverse_full(g_lat, g_lng)
                if addr:
                    ss[f"addr{fid}"] = addr
                    acc = gps.get("accuracy")
                    ss.addr_msg = ("ok", addr + (f"  (accuracy about {acc:.0f} m)" if acc else ""))
                else:
                    ss.addr_msg = ("warn", f"Location found ({g_lat:.5f}, {g_lng:.5f}) but no street address could be "
                                           "looked up. Please type it in.")
                auth = find_nearest_municipality(g_lat, g_lng, raw_details)
                ss.nearest_auth = auth
                ss[f"auth{fid}"] = auth["email"]
                ss.last_detected_pin = list(fix)
                st.rerun()

        ac1, ac2 = st.columns([3, 1])
        address = ac1.text_input("Address or landmark", key=f"addr{fid}")
        if ac2.button("🔍 Locate"):
            if address.strip():
                try:
                    geo = Nominatim(user_agent=NOMINATIM_UA, timeout=8)
                    loc = geo.geocode(address.strip(), language="en")
                    if loc:
                        ss.pin = [loc.latitude, loc.longitude]
                        raw_details = getattr(loc, "raw", {}).get("address", {})
                        auth = find_nearest_municipality(loc.latitude, loc.longitude, raw_details)
                        ss.nearest_auth = auth
                        ss[f"auth{fid}"] = auth["email"]
                        ss.last_detected_pin = [loc.latitude, loc.longitude]
                        ss.addr_msg = ("ok", loc.address)
                        st.rerun()
                    else:
                        ss.addr_msg = ("warn", f"Could not find coordinates for '{address}'. Please pick on the map.")
                except Exception:
                    ss.addr_msg = ("warn", "Address lookup failed. Please drop a pin on the map.")

        if ss.addr_msg:
            kind, text = ss.addr_msg
            (st.success if kind == "ok" else st.warning)(
                f"Detected address: {text}" if kind == "ok" else text)
        if ss.pin:
            st.button("Fill address & municipality from the pin on the map", on_click=fill_address_from_pin)
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
                addr, raw_details = _reverse_full(click["lat"], click["lng"])
                if addr:
                    ss[f"addr{fid}"] = addr
                auth = find_nearest_municipality(click["lat"], click["lng"], raw_details)
                ss.nearest_auth = auth
                ss[f"auth{fid}"] = auth["email"]
                ss.last_detected_pin = list(new_pin)
                st.rerun()

        c1, c2 = st.columns(2)
        lat_in = c1.number_input("Latitude", value=float(ss.pin[0]) if ss.pin else 0.0,
                                 format="%.5f", key=f"lat{fid}_{ss.pin}")
        lng_in = c2.number_input("Longitude", value=float(ss.pin[1]) if ss.pin else 0.0,
                                 format="%.5f", key=f"lng{fid}_{ss.pin}")
        if (lat_in or lng_in) and ss.pin != [lat_in, lng_in] and -90 <= lat_in <= 90 and -180 <= lng_in <= 180:
            ss.pin = [lat_in, lng_in]
            addr, raw_details = _reverse_full(lat_in, lng_in)
            if addr:
                ss[f"addr{fid}"] = addr
            auth = find_nearest_municipality(lat_in, lng_in, raw_details)
            ss.nearest_auth = auth
            ss[f"auth{fid}"] = auth["email"]
            ss.last_detected_pin = [lat_in, lng_in]
            st.rerun()

        # duplicate check (same problem type, within DUP_RADIUS_M)
        if ss.pin:
            dup = find_duplicate(reports, *ss.pin, category)
            if dup:
                st.warning(
                    f"A similar report **{dup['ref']}** ({cat_of(dup)}) already exists within "
                    f"{DUP_RADIUS_M} m ({dup.get('votes', 0)} upvotes)."
                )
                if st.button("Upvote it instead"):
                    for rep in reports:
                        if rep["ref"] == dup["ref"]:
                            rep["votes"] = rep.get("votes", 0) + 1
                    save_reports(reports)
                    st.success("Thanks, your upvote was added.")

        st.markdown("**4. Date and time**")
        d1, d2, d3 = st.columns([2, 2, 2])
        curr_dt = get_local_now()
        today = curr_dt.date()
        when_date = d1.date_input("Date", value=today, max_value=today, format="DD/MM/YYYY", key=f"date{fid}")
        when_time = d2.time_input("Time", value=curr_dt.time().replace(second=0, microsecond=0),
                                  format="12h", key=f"time{fid}")
        severity = d3.selectbox("Severity", ["Small", "Medium", "Dangerous"], index=1, key=f"sev{fid}")

        est = target_days(category, severity)
        st.info(
            f"Expected resolution for this problem: within **{human_days(est)}** "
            f"(target date {fmt_date(today + timedelta(days=est))}). "
            "This is a target, not a guarantee."
        )

        notes = st.text_area("Notes (optional)", key=f"notes{fid}", height=70)

        # 5. Municipal Authority & Contact
        curr_coords = ss.pin or CENTER
        if ss.nearest_auth is None:
            raw_details = get_address_details(*curr_coords)
            ss.nearest_auth = find_nearest_municipality(curr_coords[0], curr_coords[1], raw_details)
            if f"auth{fid}" not in ss or not ss[f"auth{fid}"]:
                ss[f"auth{fid}"] = ss.nearest_auth["email"] if not DEFAULT_AUTH_EMAIL else DEFAULT_AUTH_EMAIL

        curr_auth = ss.nearest_auth
        st.markdown("**5. Municipal Authority & Contact**")
        if curr_auth:
            dist_km = curr_auth.get("distance_km")
            dist_badge = f"~{dist_km} km away" if dist_km is not None else "detected"
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 8px; padding: 11px 15px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap;">
                        <div>
                            <span style="color: #60a5fa; font-weight: 600; font-size: 0.92rem;">🏛️ Nearest Municipal Office:</span>
                            <span style="color: #f8fafc; font-weight: 600; font-size: 0.95rem; margin-left: 6px;">{curr_auth['name']}</span>
                            <span style="background: rgba(59, 130, 246, 0.25); color: #bfdbfe; font-size: 0.75rem; padding: 2px 7px; border-radius: 10px; margin-left: 6px;">{dist_badge}</span>
                        </div>
                        <div style="color: #cbd5e1; font-size: 0.8rem; margin-top: 3px;">
                            📞 Helpline: <b>{curr_auth.get('helpline', '1533')}</b>
                        </div>
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 5px;">
                        Official complaint inbox: <span style="color: #38bdf8; font-family: monospace; background: rgba(0,0,0,0.3); padding: 1px 5px; border-radius: 4px;">{curr_auth['email']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        col_redetect, col_search = st.columns([1, 1])
        if col_redetect.button("🔄 Re-detect nearest office", key=f"redetect_{fid}", use_container_width=True):
            tgt_coords = ss.pin or CENTER
            raw = get_address_details(*tgt_coords)
            auth = find_nearest_municipality(tgt_coords[0], tgt_coords[1], raw)
            ss.nearest_auth = auth
            ss[f"auth{fid}"] = auth["email"]
            st.rerun()

        with col_search.expander("🏛️ Choose other civic body", expanded=False):
            st.caption("Select from major municipal authorities across India:")
            search_txt = st.text_input("Filter by city / authority", key=f"auth_search_{fid}")
            matched_auths = search_authorities(search_txt, limit=6)
            for m_auth in matched_auths:
                btn_c1, btn_c2 = st.columns([3, 1])
                btn_c1.markdown(f"**{m_auth['name']}**  \n`{m_auth['email']}`")
                if btn_c2.button("Select", key=f"btn_sel_{m_auth['short']}_{fid}"):
                    ss.nearest_auth = m_auth
                    ss[f"auth{fid}"] = m_auth["email"]
                    st.rerun()

        if curr_auth and curr_auth.get("alt_emails"):
            with st.expander("Show alternative department emails for this authority", expanded=False):
                st.caption(f"Other official emails for {curr_auth['name']}:")
                for alt_e in curr_auth["alt_emails"]:
                    clean_alt = alt_e.split(" ")[0]
                    alt_c1, alt_c2 = st.columns([3, 1])
                    alt_c1.code(alt_e)
                    if alt_c2.button("Use this", key=f"use_alt_{clean_alt}_{fid}"):
                        ss[f"auth{fid}"] = clean_alt
                        st.rerun()

        e1, e2 = st.columns(2)
        authority = e1.text_input(
            "Authority email",
            placeholder="municipal complaint email",
            key=f"auth{fid}",
            help="Auto-filled with the nearest municipality office email. You can also edit it manually."
        )
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
            if when > get_local_now() + timedelta(minutes=2):
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
                now = get_local_now()
                auth_name = curr_auth.get("name") if curr_auth else "Municipal Authority"
                rec = {
                    "ref": ref, "category": category, "lat": lat, "lng": lng, "pinned": ss.pin is not None,
                    "address": address.strip(), "when": when.strftime("%d/%m/%Y, %I:%M %p"),
                    "severity": severity, "notes": notes.strip(), "contact": contact.strip(),
                    "authority_name": auth_name,
                    "authority_email": authority.strip(),
                    "photo": photo_path, "status": 0, "votes": 0,
                    "created": now.isoformat(timespec="seconds"),
                    "target_days": est, "due": (now.date() + timedelta(days=est)).isoformat(),
                }
                reports.append(rec)
                save_reports(reports)
                ss.last = (rec, authority.strip())
                st.rerun()


# ---------- MAP ----------
with tab_map:
    st.subheader("Reports map")
    flt = st.selectbox("Show", ["All problems"] + list(CATEGORIES), key="mapfilter")
    shown = [r for r in reports if flt == "All problems" or cat_of(r) == flt]

    resolved = sum(1 for r in shown if r["status"] >= 4)
    overdue = sum(1 for r in shown if is_overdue(r))
    a, b, c, d = st.columns(4)
    a.metric("Total", len(shown))
    b.metric("Open", len(shown) - resolved)
    c.metric("Overdue", overdue)
    d.metric("Resolved", resolved)

    big = folium.Map(location=CENTER, zoom_start=12)
    for r in shown:
        folium.Marker(
            [r["lat"], r["lng"]],
            popup=f"{r['ref']} · {cat_of(r)} · {STATUSES[r['status']]} · {deadline_text(r)}",
            icon=folium.Icon(color=status_color(r["status"])),
        ).add_to(big)
    st_folium(big, height=420, use_container_width=True, returned_objects=[], key="bigmap")
    st.caption("Red: submitted. Orange: in progress. Green: resolved.")

    st.markdown("**Recent reports**")
    if not shown:
        st.write("No reports yet.")
    for r in reversed(shown[-8:]):
        col_img, col_txt = st.columns([1, 4])
        if Path(r["photo"]).exists():
            col_img.image(r["photo"], width=70)
        col_txt.markdown(
            f"**{r['ref']}** · {cat_of(r)} · {STATUSES[r['status']]}  \n"
            f"{r['address'] or 'Pinned location'} · {r['severity']} · {r.get('votes', 0)} upvotes  \n"
            f"Target: {fmt_date(due_date(r))} ({deadline_text(r)})"
        )


# ---------- TRACK ----------
with tab_track:
    st.subheader("Track a complaint")
    ref_in = st.text_input("Reference number", placeholder="CC-2026-123456").strip().upper()
    if ref_in:
        rep = next((r for r in reports if r["ref"] == ref_in), None)
        if rep is None:
            st.error("No report found with that reference on this machine.")
        else:
            st.markdown(f"### {rep['ref']} · {STATUSES[rep['status']]}")
            auth_info = f" · Authority: **{rep['authority_name']}** ({rep.get('authority_email', '')})" if rep.get("authority_name") else ""
            st.caption(f"{cat_of(rep)} · {rep['address'] or 'Pinned location'} · {rep['severity']} · "
                       f"{rep.get('votes', 0)} upvotes{auth_info} · observed {format_when(rep.get('when', ''))}")


            due = due_date(rep)
            total = rep.get("target_days") or target_days(cat_of(rep), rep.get("severity", "Medium"))
            if rep["status"] >= 4:
                done = rep.get("resolved_on")
                if done:
                    late = (date.fromisoformat(done) - due).days
                    st.success(f"Resolved on {fmt_date(date.fromisoformat(done))} "
                               + ("(within the target time)." if late <= 0
                                  else f"({late} day{'s' if late != 1 else ''} after the target date)."))
                else:
                    st.success("Resolved.")
            elif is_overdue(rep):
                st.error(f"Target date was {fmt_date(due)}. This report is {deadline_text(rep)}.")
            else:
                st.info(f"Target: within {human_days(total)}, by {fmt_date(due)} ({deadline_text(rep)}). "
                        "This is a target, not a guarantee.")

            if Path(rep["photo"]).exists():
                st.image(rep["photo"], width=240)
            st.progress((rep["status"] + 1) / len(STATUSES))
            for i, s in enumerate(STATUSES):
                st.markdown(f"{'✅' if i <= rep['status'] else '⬜'} {s}")
            if rep["status"] < 4:
                if st.button("Demo: advance status"):
                    rep["status"] += 1
                    if rep["status"] >= 4:
                        rep["resolved_on"] = get_local_now().date().isoformat()
                    save_reports(reports)
                    st.rerun()
                st.caption("In a live system the municipality updates this. The button only simulates it.")

st.divider()
st.caption("Demo build: data is stored on this machine only.")