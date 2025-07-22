# ui_student.py

import streamlit as st
from datetime import datetime
import pytz
import pandas as pd
from bookings import save_bookings
from email_utils import send_confirmation_email

def show_student_signup(bookings_df, slo_slots_by_day, ncc_slots_by_day, now):
    st.title("Student AT Appointment Sign-Up")

    st.markdown("""
    **Please read before booking:**
    - You may sign up for either location (SLO or NCC) 
    - Once booked, you will receive email confirmation.
    - You may only sign up for **one appointment per week**.
    - DSPS students may book a **double time block** if needed.
    - You can reschedule future appointments, but you **cannot reschedule on the day** of your scheduled appointment.
    """)

    # Timezone
    pacific = pytz.timezone("US/Pacific")

    # UI Inputs
    lab_location = st.selectbox("Choose your AT Lab location:", ["SLO AT Lab", "NCC AT Lab"])
    slots_by_day = slo_slots_by_day if lab_location == "SLO AT Lab" else ncc_slots_by_day

    name = st.text_input("Full Name")
    email = st.text_input("Cuesta Email")
    student_id = st.text_input("Student ID")
    dsps = st.checkbox("I am a DSPS student")

    if email and not (email.lower().endswith("@my.cuesta.edu") or email.lower().endswith("@cuesta.edu")):
        st.error("Please use your official Cuesta email ending in @my.cuesta.edu or @cuesta.edu")
        return

    if student_id and not student_id.startswith("900"):
        st.error("Student ID must start with 900.")
        return

    if not (name and email and student_id):
        return

    selected_day = st.selectbox("Choose a day:", list(slots_by_day.keys()))
    
    available_slots = [
        s for s in slots_by_day[selected_day]
        if s not in bookings_df["slot"].values and
        pacific.localize(datetime.strptime(f"{s.split()[1]} {s.split()[2].split('–')[0]} {s.split()[3]}", "%m/%d/%y %I:%M %p")) > now
    ]

    double_blocks = {}
    for i in range(len(slots_by_day[selected_day]) - 1):
        s1 = slots_by_day[selected_day][i]
        s2 = slots_by_day[selected_day][i + 1]
        if s1.split()[1] == s2.split()[1]:
            double_blocks[f"{s1} and {s2}"] = [s1, s2]

    # Booking Flow
    if dsps:
        valid_blocks = [label for label in double_blocks if all(s not in bookings_df["slot"].values for s in double_blocks[label])]
        selected_block = st.selectbox("Choose a double time block:", valid_blocks) if valid_blocks else None
        if selected_block and st.button("Book Appointment"):
            confirm_booking(
                selected_block,
                bookings_df,
                name,
                email,
                student_id,
                dsps,
                lab_location,
                double_blocks[selected_block],
                now
            )
    else:
        selected_time = st.selectbox("Choose a time:", available_slots) if available_slots else None
        if selected_time and st.button("Book Appointment"):
            confirm_booking(
                selected_time,
                bookings_df,
                name,
                email,
                student_id,
                dsps,
                lab_location,
                [selected_time],
                now
            )

def confirm_booking(selected_slot_label, bookings_df, name, email, student_id, dsps, lab_location, slots_to_book, now):
    week_of_slot = datetime.strptime(slots_to_book[0].split(" ")[1], "%m/%d/%y").isocalendar().week

    existing_bookings = bookings_df[bookings_df["email"] == email]
    booked_weeks = existing_bookings["slot"].apply(lambda s: datetime.strptime(s.split(" ")[1], "%m/%d/%y").isocalendar().week)

    block_reschedule = False
    updated_indices = []

    for i, row in existing_bookings.iterrows():
        existing_date = datetime.strptime(row["slot"].split(" ")[1], "%m/%d/%y").date()
        existing_week = existing_date.isocalendar().week

        if existing_date == now.date() and existing_week == week_of_slot:
            block_reschedule = True
            break
        if existing_week == week_of_slot and existing_date != now.date():
            updated_indices.append(i)

    if block_reschedule:
        st.warning("You already have a booking today. Rescheduling to another day is not allowed once the day has begun.")
        return

    # Remove prior bookings for same week (except today)
    bookings_df.drop(updated_indices, inplace=True)

    # Add new slot(s)
    for slot in slots_to_book:
        new_row = pd.DataFrame([{
            "name": name,
            "email": email,
            "student_id": student_id,
            "dsps": dsps,
            "slot": slot,
            "lab_location": lab_location
        }])
        bookings_df = pd.concat([bookings_df, new_row], ignore_index=True)

    save_bookings(bookings_df)
    send_confirmation_email(email, name, selected_slot_label, lab_location)
    st.success(f"Successfully booked: {selected_slot_label}")
