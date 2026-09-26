from datetime import datetime
from Components.Badge import Badge


def DateRangeBadge(start_date, end_date, show_progress=True):
    """
    Create a "{start} - {end}" badge for Date Applied -> Expected Response Date

    Args:
        start_date: Date applied (mm/dd/yy)
        end_date: Expected response date (mm/dd/yy)
        show_progress: Color the badge by how much of the waiting period has elapsed
                       (green -> orange -> red -> dark red when past due). When False,
                       or if the dates can't be parsed, a plain gray badge is used.

    Returns:
        QLabel styled as a badge
    """
    text = f"{start_date} - {end_date}"

    if not show_progress:
        return Badge(text)

    try:
        start_date_obj = datetime.strptime(start_date, "%m/%d/%y")
        end_date_obj = datetime.strptime(end_date, "%m/%d/%y")
    except (TypeError, ValueError):
        return Badge(text)

    # Calculate progress ratio through the waiting period
    total_duration = (end_date_obj - start_date_obj).total_seconds()
    elapsed_time = (datetime.now() - start_date_obj).total_seconds()
    progress_ratio = elapsed_time / total_duration if total_duration > 0 else 0

    if progress_ratio < 0:
        # Not started yet
        return Badge(text)
    elif progress_ratio < 1/3:
        background = "#4CAF50"  # First third - green
    elif progress_ratio < 2/3:
        background = "#FF9800"  # Second third - orange
    elif progress_ratio <= 1:
        background = "#f44336"  # Final third - red
    else:
        background = "#c62828"  # Past due - dark red

    return Badge(text, color="white", background=background, weight="bold")
