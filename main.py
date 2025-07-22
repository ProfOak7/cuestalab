# main.py

import streamlit as st
from datetime import datetime
import pytz

from bookings import load_bookings
from slots import generate_slots
from ui_student import show_student_signup
from ui_admin import show_admin_view
from email_utils import init_email  # Optional, for future Gmail setup

# --- Configuration ---
st.set_page_config(page_title="Student Appointment Sign-Up", layout="wide")

# --- Secrets ---
ADMIN_PASSCODE = st.secrets["ADMIN_PASSCODE"]
AVAILABILITY_PASSCODE = st.secrets["AVAILABILITY_PASSCODE"]

# --- Timezone ---
pacific = pytz.timezone("US/Pacific")
now = datetime.now(pacific)

# --- Load data ---
bookings_df = load_bookings()
slo_slots_by_day, ncc_slots_by_day = generate_slots()

# --- Navigation ---
st.sidebar.title("Navigation")
selected_tab = st.sidebar.radio("Go to:", ["Sign-Up", "Admin View", "Availability Settings"])

# --- View Routing ---
if selected_tab == "Sign-Up":
    show_student_signup(bookings_df, slo_slots_by_day, ncc_slots_by_day, now)

elif selected_tab == "Admin View":
    show_admin_view(bookings_df, slo_slots_by_day, ncc_slots_by_day, ADMIN_PASSCODE)

elif selected_tab == "Availability Settings":
    st.write("Coming soon!")
