# ui_admin.py

import streamlit as st
from datetime import datetime
import pandas as pd
from bookings import save_bookings

def show_admin_view(bookings_df, slo_slots_by_day, ncc_slots_by_day, admin_passcode):
    st.title("Admin Panel")
    entered_passcode = st.text_input("Enter admin passcode:", type="password")

    if entered_passcode != admin_passcode:
        if entered_passcode:
            st.error("Incorrect passcode.")
        return

    st.success("Access granted.")

    # Show lab bookings
    for lab in ["SLO AT Lab", "NCC AT Lab"]:
        lab_df = bookings_df[bookings_df["lab_location"] == lab]
        st.subheader(f"{lab} Bookings")
        st.dataframe(lab_df)
        st.download_button(f"Download {lab} Bookings", lab_df.to_csv(index=False), file_name=f"{lab.lower().replace(' ', '_')}_bookings.csv")

    # Show today's bookings
    today_str = datetime.today().strftime("%m/%d/%y")
    for lab in ["SLO AT Lab", "NCC AT Lab"]:
        lab_df = bookings_df[bookings_df["lab_location"] == lab]
        today_df = lab_df[lab_df["slot"].str.contains(today_str)].copy()
        if not today_df.empty:
            today_df["slot_dt"] = today_df["slot"].apply(lambda s: datetime.strptime(f"{s.split()[1]} {s.split()[2].split('–')[0]} {s.split()[3]}", "%m/%d/%y %I:%M %p"))
            today_df.sort_values("slot_dt", inplace=True)
            today_df.drop(columns=["slot_dt"], inplace=True)
            st.download_button(f"Download Today's {lab} Appointments", today_df.to_csv(index=False), file_name=f"todays_{lab.lower().replace(' ', '_')}_appointments.csv")
        else:
            st.info(f"No {lab} appointments scheduled for today.")

    # Rescheduling Tool
    st.subheader("Reschedule a Student Appointment")

    if bookings_df.empty:
        st.info("No appointments to reschedule.")
        return

    booking_options = [f"{row['name']} ({row['email']}) - {row['slot']}" for _, row in bookings_df.iterrows()]
    selected_option = st.selectbox("Select a booking to reschedule", booking_options)

    selected_index = booking_options.index(selected_option)
    current_booking = bookings_df.iloc[selected_index]

    lab_slots = slo_slots_by_day if current_booking["lab_location"] == "SLO AT Lab" else ncc_slots_by_day
    current_slot = current_booking["slot"]

    available_by_day = {
        day: [s for s in slots if s not in bookings_df["slot"].values or s == current_slot]
        for day, slots in lab_slots.items()
    }
    days_with_slots = [day for day, slots in available_by_day.items() if slots]

    selected_day = st.selectbox("Choose a new day:", days_with_slots)
    selected_time = st.selectbox("Choose a new time:", available_by_day[selected_day])

    if st.button("Reschedule"):
        if current_booking["dsps"] and bookings_df[bookings_df["email"] == current_booking["email"]].shape[0] == 2:
            # DSPS rescheduling: move both blocks
            old_slots = bookings_df[bookings_df["email"] == current_booking["email"]]["slot"].tolist()
            bookings_df = bookings_df[bookings_df["email"] != current_booking["email"]]

            try:
                index = lab_slots[selected_day].index(selected_time)
                new_block = [lab_slots[selected_day][index], lab_slots[selected_day][index + 1]]
            except IndexError:
                st.error("Couldn't find a valid consecutive block for DSPS rescheduling.")
                return

            for s in new_block:
                new_row = current_booking.copy()
                new_row["slot"] = s
                bookings_df = pd.concat([bookings_df, pd.DataFrame([new_row])], ignore_index=True)

            save_bookings(bookings_df)
            st.success(f"DSPS appointment successfully moved to: {new_block[0]} and {new_block[1]}")
        else:
            # Regular student rescheduling
            bookings_df.at[selected_index, "slot"] = selected_time
            save_bookings(bookings_df)
            st.success(f"Appointment rescheduled to: {selected_time}")
