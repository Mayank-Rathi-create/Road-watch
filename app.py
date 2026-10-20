"""
Civic-Connect Streamlit Entrypoint
Allows running the application via:
    streamlit run app.py
or
    streamlit run Road_Watch.py
"""
import runpy
from pathlib import Path

target_script = Path(__file__).parent / "Road_Watch.py"
if not target_script.exists():
    target_script = Path(__file__).parent / "Civic_Connect.py"
runpy.run_path(str(target_script), run_name="__main__")

