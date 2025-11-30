import streamlit as st
import requests
import datetime
import google.generativeai as genai

# -----------------------------
# API KEYS
# -----------------------------
NASA_API_KEY = "cAnQL8sTZR9PXqVkTlJJfAO2etBrIh63ojCXCwNx"

# Gemini setup
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("models/gemini-flash-latest")
else:
    model = None

# -----------------------------
# PAGE HEADER
# -----------------------------
st.title("Alien Asteroid Chatbot 👽")
st.write("Load real NASA asteroid data and chat with a friendly alien about it!")

# -----------------------------
# USER INPUTS FOR NASA DATA
# -----------------------------
date = st.date_input("Select a date", value=datetime.date.today())
min_diameter = st.slider("Minimum diameter (m)", 0.0, 2000.0, 0.0, 10.0)
hazard_only = st.checkbox("Only hazardous asteroids")

# -----------------------------
# LOAD ASTEROID DATA
# -----------------------------
if st.button("Load asteroid data"):
    nasa_date = date.strftime("%Y-%m-%d")
    url = (
        "https://api.nasa.gov/neo/rest/v1/feed"
        f"?start_date={nasa_date}&end_date={nasa_date}&api_key={NASA_API_KEY}"
    )

    with st.spinner("Fetching NASA asteroid data..."):
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            raw = response.json()
        except Exception as e:
            st.error(f"NASA API error: {e}")
            st.stop()

    # Get asteroid list safely
    neos = raw.get("near_earth_objects", {}).get(nasa_date, [])
    filtered = []

    for neo in neos:
        try:
            diameter = neo["estimated_diameter"]["meters"]["estimated_diameter_max"]
            hazardous = neo["is_potentially_hazardous_asteroid"]

            if diameter < min_diameter:
                continue
            if hazard_only and not hazardous:
                continue

            close = neo["close_approach_data"][0]

            filtered.append({
                "name": neo["name"],
                "diameter_m": diameter,
                "hazardous": hazardous,
                "velocity_km_s": float(close["relative_velocity"]["kilometers_per_second"]),
                "miss_distance_km": float(close["miss_distance"]["kilometers"]),
            })
        except Exception:
            continue

    # Store to session_state
    st.session_state["asteroid_data"] = filtered
    st.session_state["asteroid_date"] = nasa_date

# -----------------------------
# DISPLAY SUMMARY
# -----------------------------
data = st.session_state.get("asteroid_data", [])
date_str = st.session_state.get("asteroid_date", "")

if data:
    st.subheader("Loaded Asteroid Data")
    st.write(f"Date: **{date_str}**")
    st.write(f"Asteroids Loaded: **{len(data)}**")
    st.write(f"Hazardous: **{sum(a['hazardous'] for a in data)}**")
else:
    st.info("Load asteroid data to chat with the alien.")
    st.stop()

st.divider()

# -----------------------------
# CHATBOT SECTION
# -----------------------------
st.subheader("Chat with the Alien 👽")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# show previous messages
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(msg)

user_msg = st.chat_input("Ask the alien anything about these asteroids:")

if user_msg:
    st.session_state.chat_history.append(("user", user_msg))

    if model is None:
        answer = "Gemini API key missing! Add it to secrets.toml."
        st.session_state.chat_history.append(("assistant", answer))
        with st.chat_message("assistant"):
            st.write(answer)
        st.stop()

    # prepare asteroid summary
    summary = "\n".join([
        f"{a['name']} — {a['diameter_m']:.1f} m, "
        f"{a['velocity_km_s']:.2f} km/s, "
        f"miss {a['miss_distance_km']:.0f} km, "
        f"hazardous={a['hazardous']}"
        for a in data[:10]
    ])

    # conversation summary
    history = "\n".join(f"{r}: {m}" for r, m in st.session_state.chat_history)

    prompt = f"""
You are a friendly alien explaining asteroid data.

ASTEROIDS:
{summary}

CONVERSATION SO FAR:
{history}

HUMAN ASKED:
"{user_msg}"

Answer clearly, in 1–3 short paragraphs.
"""

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            answer = f"Gemini API error: {e}"

        st.write(answer)
        st.session_state.chat_history.append(("assistant", answer))
