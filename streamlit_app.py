"""Streamlit Cloud entry point — launches the Gradio app."""
import startup; startup.build_if_needed()
from app import demo
demo.launch()
