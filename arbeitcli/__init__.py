import json
import os
import time
from termcolor import colored
from datetime import date
from datetime import timedelta

def db_file():
    return os.environ["ARBEIT_PATH"] + "/arbeit.json"

def load_db():
    if os.path.isfile(db_file()):
        return json.load(open(db_file()))
    else:
        return {
            "lock_version": "1",
            "dates": {}
        }

def write_db(db):
    with open(db_file(), 'w') as outfile:
        json.dump(db, outfile, indent=2, sort_keys=True)

def today():
    return time.strftime("%Y-%m-%d")

def find_date(db, date):
    try:
        return db["dates"][date]
    except KeyError:
        return {"start": None, "end": None, "breaks": [], "comment": None}

def replace_today(db, data):
    db["dates"][today()] = data

def hours_to_minutes(date):
    parts = date.split(":")
    return int(parts[0]) * 60 + int(parts[1])

def minutes_to_hours(minutes):
    return "%s%.2d:%.2d" % ("-" if minutes < 0 else "", abs(minutes) / 60, abs(minutes) % 60)

def calculate_working_hours(date):
    if (date["end"] == None) or (date["start"] == None):
        return 0

    duration = hours_to_minutes(date["end"]) - hours_to_minutes(date["start"])

    breaks = 0
    for b in date["breaks"]:
        breaks += hours_to_minutes(b["end"]) - hours_to_minutes(b["start"])

    return duration - breaks

def show_date(date):
    print(" Start: %s" % (date["start"] if date["start"] else colored("missing", "red")))
    print("   End: %s" % (date["end"] if date["end"] else colored("missing", "red")))
    if len(date["breaks"]) > 0:
        print
        print("Breaks:")
        for b in date["breaks"]:
            if b["comment"]:
                comment = " (%s)" % b["comment"]
            else:
                comment = ""
            print("  %s - %s%s" % (b["start"], b["end"], comment))
    print
    if date["start"] and date["end"]:
        working_hours = calculate_working_hours(date)
        print("= %s" % show_diff(working_hours, 8 * 60))
    elif date["start"]:
        date["end"] = now()
        working_hours = calculate_working_hours(date)
        print("So far %s" % show_diff(working_hours, 8 * 60))

def show_diff(result, required):
    difference = result - required
    return "%s (%s)" % (
        minutes_to_hours(result),
        colored(minutes_to_hours(difference), 'green' if result > required else 'yellow')
    )

def now():
    return time.strftime("%H:%M")

def set_time(time_field, time, force):
    db = load_db()
    d = find_date(db, today())
    if d[time_field]:
        if force:
            print(colored('Overwriting previous %s time (was %s).' % (time_field, d[time_field]), 'yellow'))
        else:
            print(colored('%s time already set to %s. Use "--force" to overwrite.' % (time_field.title(), d[time_field]), 'red'))
            return

    if time:
        d[time_field] = time
    else:
        d[time_field] = now()

    replace_today(db, d)
    write_db(db)

def add_break(start, end, comment):
    if not end:
        end = now()

    db = load_db()
    d = find_date(db, today())

    d["breaks"].append({
        "start": start,
        "end": end,
        "comment": comment
    })

    replace_today(db, d)
    write_db(db)

def calc_week_data(db, calendar_week, year):
    days_in_week = days_in_calendar_week(calendar_week, year)
    week_data = {"days": [], "sum": 0}

    for d in days_in_week:
        item = {}
        item["date"] = d
        item["minutes"] = calculate_working_hours(find_date(db, d.strftime('%Y-%m-%d')))
        week_data["days"].append(item)
        week_data["sum"] += item["minutes"]

    return week_data

def days_in_month(month):
    # make the index directly indexable by having a fake first item
    month_days_mapping = [None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return month_days_mapping[month]

def days_in_year(year):
    days = []
    for month in range(1, 12 + 1):
        for day in range(1, days_in_month(month) + 1):
            days.append(date(year, month, day))
    return days

def days_in_calendar_week(calendar_week, year):
    def matching_calendar_week(d):
        return d.isocalendar()[1] == calendar_week

    return filter(matching_calendar_week, days_in_year(year))
