from datetime import datetime, timedelta
from typing import Dict, Any

def parse_date_filters(date_text: str) -> Dict[str, Any]:
    """
    Parse natural language date filters into database query parameters
    """
    date_text = date_text.lower().strip()
    today = datetime.now().date()
    
    filters = {}
    
    if "today" in date_text:
        filters["date_from"] = today
        filters["date_to"] = today + timedelta(days=1)
    
    elif "yesterday" in date_text:
        yesterday = today - timedelta(days=1)
        filters["date_from"] = yesterday
        filters["date_to"] = today
    
    elif "this_week" in date_text:
        # Start of current week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        filters["date_from"] = start_of_week
        filters["date_to"] = end_of_week
    
    elif "last_week" in date_text:
        # Previous week
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=7)
        filters["date_from"] = start_of_last_week
        filters["date_to"] = end_of_last_week
    
    elif "this_month" in date_text:
        # Current month
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1)
        filters["date_from"] = start_of_month
        filters["date_to"] = end_of_month
    
    elif "last_month" in date_text:
        # Previous month
        if today.month == 1:
            start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
        else:
            start_of_last_month = today.replace(month=today.month - 1, day=1)
        end_of_last_month = today.replace(day=1)
        filters["date_from"] = start_of_last_month
        filters["date_to"] = end_of_last_month
    
    return filters

def format_date_for_display(date_obj: datetime) -> str:
    """Format date for user-friendly display"""
    return date_obj.strftime("%d %B %Y, %I:%M %p")

def get_relative_date_text(date_obj: datetime) -> str:
    """Get relative date text like '2 days ago'"""
    now = datetime.now()
    diff = now - date_obj
    
    if diff.days == 0:
        if diff.seconds < 3600:
            return "just now"
        elif diff.seconds < 7200:
            return "1 hour ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
    elif diff.days == 1:
        return "yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} weeks ago"
    else:
        months = diff.days // 30
        return f"{months} months ago" 