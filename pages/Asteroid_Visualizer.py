import streamlit as st
import requests
import pandas as pd
import datetime
import google.generativeai as genai

# -----------------------------
# API KEYS
# -----------------------------
NASA_API_KEY = "cAnQL8sTZR9PXqVkTlJJfAO2etBrIh63ojCXCwNx"

# Gemini key must be in .streamlit/secrets.toml
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("models/gemini-flash-latest")
else:
    model = None

# -----------------------------
# PAGE HEADER
# -----------------------------
st.title("Asteroid Visualizer – LLM Summary")

st.write("""
This page fetches NASA asteroid data and asks Google Gemini to summarize it.
""")

# -----------------------------
# USER INPUTS
# -----------------------------
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", value=datetime.date.today())
with col2:
    days = st.slider("Number of days", 1, 7, 3)

min_diameter = st.slider(
    "Minimum asteroid diameter (meters)",
    0.0, 2000.0, 50.0, 10.0
)

style = st.selectbox(
    "Writing style",
    ["Scientific report", "News article", "Kid-friendly explanation"]
)

hazard_only = st.checkbox("Only hazardous asteroids")

# -----------------------------
# MAIN BUTTON
# -----------------------------
if st.button("Fetch data and generate summary"):

    # Step 1 — NASA API CALL
    end_date = start_date + datetime.timedelta(days=days - 1)
    url = (
        "https://api.nasa.gov/neo/rest/v1/feed"
        f"?start_date={start_date}&end_date={end_date}&api_key={NASA_API_KEY}"
    )

    with st.spinner("Fetching NASA data..."):
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            raw = resp.json()
        except Exception as e:
            st.error(f"NASA API error: {e}")
            st.stop()

    # Step 2 — PROCESS DATA
    rows = []
    for date_str, neos in raw.get("near_earth_objects", {}).items():
        for neo in neos:
            try:
                d = neo["estimated_diameter"]["meters"]["estimated_diameter_max"]
                hazard = neo["is_potentially_hazardous_asteroid"]
                if d < min_diameter: continue
                if hazard_only and not hazard: continue

                close = neo["close_approach_data"][0]
                rows.append({
                    "date": date_str,
                    "name": neo["name"],
                    "diameter_m": d,
                    "hazardous": hazard,
                    "velocity_km_s": float(close["relative_velocity"]["kilometers_per_second"]),
                    "miss_distance_km": float(close["miss_distance"]["kilometers"])
                })
            except:
                continue

    if not rows:
        st.warning("No asteroids matched the filters.")
        st.stop()

    df = pd.DataFrame(rows).sort_values("diameter_m", ascending=False)

    # Step 3 — DISPLAY
    st.subheader("Asteroid Table")
    st.dataframe(df, use_container_width=True)

    st.subheader("Asteroid Sizes (m)")
    st.bar_chart(df, x="name", y="diameter_m")

    # Step 4 — GEMINI SUMMARY
    if model is None:
        st.error("Missing Gemini key in secrets.toml")
        st.stop()

    data_summary = df.to_csv(index=False)

    prompt = f"""
Write a {style.lower()} summarizing this NASA asteroid dataset.

DATA:
{data_summary}
"""

    with st.spinner("Asking Gemini..."):
        try:
            response = model.generate_content(prompt)
            st.write(response.text)
        except Exception as e:
            st.error(f"Gemini API error: {e}")
