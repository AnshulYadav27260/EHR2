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
import os
import sqlite3

# Simulating Real-Time Monitoring Data Over 12 Months for Departments
months = [f"Month {i}" for i in range(1, 13)]
departments = ["Radiology", "Emergency", "Cardiology", "Internal Medicine"]

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("cdss_dashboard.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS corrective_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric TEXT,
                    root_causes TEXT,
                    action_taken TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

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
    def save_corrective_action(metric, root_causes, action_taken):
        conn = sqlite3.connect("cdss_dashboard.db")
        c = conn.cursor()
        c.execute("INSERT INTO corrective_actions (metric, root_causes, action_taken) VALUES (?, ?, ?)",
                  (metric, root_causes, action_taken))
        conn.commit()
        conn.close()

    def get_corrective_actions():
        conn = sqlite3.connect("cdss_dashboard.db")
        c = conn.cursor()
        c.execute("SELECT id, metric, root_causes, action_taken, timestamp FROM corrective_actions")
        data = c.fetchall()
        conn.close()
        df = pd.DataFrame(data, columns=["ID", "Metric", "Root Causes", "Action Taken", "Timestamp"])
        return df if not df.empty else pd.DataFrame(columns=["ID", "Metric", "Root Causes", "Action Taken", "Timestamp"])

    def automated_corrective_actions(metric, root_causes):
        actions = {
            "Adoption Rate (%)": "Enhance CDSS training, improve user experience, and incentivize usage.",
            "Physician Satisfaction (%)": "Conduct feedback sessions, optimize alert frequency, and improve CDSS usability.",
            "Alert Fatigue Score (Lower is Better)": "Refine alert prioritization, reduce non-essential notifications, and implement AI-driven optimizations."
        }
        action = actions.get(metric, "No predefined corrective action available.")
        save_corrective_action(metric, root_causes, action)
        return action

    # Admin Dashboard for Corrective Actions
    st.write("### Admin Dashboard: Manage Corrective Actions")
    df_corrective_actions = get_corrective_actions()
    if df_corrective_actions.empty:
        st.warning("No corrective actions recorded yet.")
    else:
        st.dataframe(df_corrective_actions)

    # Generate and Download Reports with Data Visualization
    st.write("### Generate Administrative Report with Visuals")
    if not df_corrective_actions.empty:
        csv = df_corrective_actions.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV Report", csv, "CDSS_Corrective_Actions_Report.csv", "text/csv")

    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

else:
    st.warning("🔒 Please log in to access the dashboard.")
