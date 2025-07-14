from datetime import datetime

def hours(delta):
    hours = delta.total_seconds() / 3600
    return hours