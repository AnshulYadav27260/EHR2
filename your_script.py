import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import schedule
import time
from threading import Thread
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
from scipy.stats import zscore
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import hashlib

# Simulating Real-Time Monitoring Data Over 12 Months for Departments
months = [f"Month {i}" for i in range(1, 13)]
departments = ["Radiology", "Emergency", "Cardiology", "Internal Medicine"]

# User Authentication System
users = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "user": hashlib.sha256("user123".encode()).hexdigest()
}

# Authentication Function
def authenticate(username, password):
    if username in users and users[username] == hashlib.sha256(password.encode()).hexdigest():
        return True
    return False

# Login Page
st.sidebar.title("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

if login_button:
    if authenticate(username, password):
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
    else:
        st.sidebar.error("Invalid Username or Password")

# Restrict Access to Dashboard
if "authenticated" in st.session_state and st.session_state["authenticated"]:
    st.title(f"CDSS Real-Time Monitoring Dashboard - Welcome {st.session_state['username']}")

    # Fetching real-time data from EHR system (simulated API call)
    def fetch_live_data():
        live_data = {
            "Month": months * len(departments),
            "Department": sum([[dept] * 12 for dept in departments], []),
            "Adoption Rate (%)": sum([
                list(np.linspace(start, start + np.random.randint(5, 15), 12)) for start in [70, 60, 50, 45]
            ], []),
            "Physician Satisfaction (%)": sum([
                list(np.linspace(start, start + np.random.randint(5, 10), 12)) for start in [80, 70, 65, 60]
            ], []),
            "Alert Fatigue Score (Lower is Better)": sum([
                list(np.linspace(start, start - np.random.randint(5, 15), 12)) for start in [60, 70, 75, 80]
            ], [])
        }
        return pd.DataFrame(live_data)

    df_trend_monitoring = fetch_live_data()

    # Select Department
    selected_department = st.selectbox("Select Department:", departments)
    df_filtered = df_trend_monitoring[df_trend_monitoring["Department"] == selected_department]

    # Implement Automated Corrective Actions Tracking
    corrective_action_history = []
    
    def automated_corrective_actions(metric, root_causes):
        actions = {
            "Adoption Rate (%)": "Enhance CDSS training, improve user experience, and incentivize usage.",
            "Physician Satisfaction (%)": "Conduct feedback sessions, optimize alert frequency, and improve CDSS usability.",
            "Alert Fatigue Score (Lower is Better)": "Refine alert prioritization, reduce non-essential notifications, and implement AI-driven optimizations."
        }
        action = actions.get(metric, "No predefined corrective action available.")
        corrective_action_history.append({"Metric": metric, "Root Causes": root_causes, "Action Taken": action})
        return action

    # Display Corrective Action History
    st.write("### Corrective Action History")
    st.dataframe(pd.DataFrame(corrective_action_history))

    # Generate and Download Reports with Data Visualization
    st.write("### Generate Administrative Report with Visuals")
    if corrective_action_history:
        df_corrective_actions = pd.DataFrame(corrective_action_history)
        csv = df_corrective_actions.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV Report", csv, "CDSS_Corrective_Actions_Report.csv", "text/csv")

    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()
else:
    st.warning("🔒 Please log in to access the dashboard.")
