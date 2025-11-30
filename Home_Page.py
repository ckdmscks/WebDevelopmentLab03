import streamlit as st
from pathlib import Path

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("Web Development Lab03")

# --------------------------------------------------
# Assignment Header
# --------------------------------------------------
st.header("CS 1301")
st.subheader("Team 36, Web Development - Section C")
st.subheader("Ben Morrissey, Eunchan Daniel Cha")

# --------------------------------------------------
# Introduction
# --------------------------------------------------
st.write("""
Welcome to our Streamlit Web Development Lab03 app!  
Use the sidebar on the left to navigate between the pages.

### Pages Included:
1. **Asteroid Information** – Access real-time NASA asteroid data.  
2. **Asteroid Visualizer** – Explore visualizations of near-Earth objects.  
3. **Alien Chatbot** – Chat with an alien about asteroids and space.  
""")

# --------------------------------------------------
# Image Loading (Auto-fix for Streamlit Cloud)
# --------------------------------------------------

# Correct relative path handling
image_path = Path("images/outerspaceimage.jpeg")

if image_path.exists():
    st.image(str(image_path))
else:
    st.error("⚠️ Image not found: images/outerspaceimage.jpeg")
    st.write("Make sure the file is located in **WebDevelopmentLab03/images/**")
