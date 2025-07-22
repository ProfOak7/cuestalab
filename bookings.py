# bookings.py

import pandas as pd
import os

BOOKINGS_FILE = "bookings.csv"

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        bookings_df = pd.read_csv(BOOKINGS_FILE)
    else:
        bookings_df = pd.DataFrame(columns=["name", "email", "student_id", "dsps", "slot"])

    # Add lab_location if missing (for backward compatibility)
    if "lab_location" not in bookings_df.columns:
        bookings_df["lab_location"] = "SLO AT Lab"

    return bookings_df

def save_bookings(bookings_df):
    bookings_df.to_csv(BOOKINGS_FILE, index=False)
