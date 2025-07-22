# slots.py

from datetime import datetime, timedelta

def generate_slots():
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    days = [today + timedelta(days=i) for i in range(21)]

    slo_hours = {
        0: ("09:00", "21:00"),  # Monday
        1: ("09:00", "21:00"),  # Tuesday
        2: ("08:30", "21:00"),  # Wednesday
        3: ("08:15", "20:30"),  # Thursday
        4: ("09:15", "15:00"),  # Friday
        5: ("09:15", "13:00"),  # Saturday
    }

    ncc_hours = {
        0: ("12:00", "16:00"),  # Monday
        1: ("08:15", "20:00"),  # Tuesday
        2: ("08:15", "17:00"),  # Wednesday
        3: ("09:15", "17:00"),  # Thursday
        4: ("08:15", "15:00"),  # Friday
    }

    slo_slots_by_day = {}
    ncc_slots_by_day = {}

    for day in days:
        weekday = day.weekday()
        label_day = day.strftime('%A %m/%d/%y')

        # Generate SLO slots
        if weekday in slo_hours:
            slo_slots_by_day[label_day] = generate_day_slots(day, slo_hours[weekday])

        # Generate NCC slots
        if weekday in ncc_hours:
            ncc_slots_by_day[label_day] = generate_day_slots(day, ncc_hours[weekday])

    return slo_slots_by_day, ncc_slots_by_day


def generate_day_slots(day, hours):
    start_str, end_str = hours
    current_time = datetime.combine(day.date(), datetime.strptime(start_str, "%H:%M").time())
    end_time = datetime.combine(day.date(), datetime.strptime(end_str, "%H:%M").time())

    slots = []
    while current_time < end_time:
        slot = f"{day.strftime('%A %m/%d/%y')} {current_time.strftime('%-I:%M')}\u2013{(current_time + timedelta(minutes=15)).strftime('%-I:%M %p')}"
        slots.append(slot)
        current_time += timedelta(minutes=15)

    return slots
