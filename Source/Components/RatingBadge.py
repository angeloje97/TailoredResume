from Components.Badge import Badge


def rating_colors(value):
    """
    Get the (text color, background color) for a 1-10 score

    8+ is green, 5+ is orange, anything lower (or non-numeric) is red.
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "#c62828", "#ffebee"

    if value >= 8:
        return "#2e7d32", "#e8f5e9"  # Dark green on light green
    elif value >= 5:
        return "#ef6c00", "#fff3e0"  # Dark orange on light orange
    else:
        return "#c62828", "#ffebee"  # Dark red on light red


def RatingBadge(icon, value, font_size=10):
    """
    Create a "{icon} {value}/10" badge colored by score (used for Match Rating and Job Quality)

    Args:
        icon: Emoji prefix, e.g. "⭐" for Match Rating or "💎" for Job Quality
        value: Score from 1-10
        font_size: Font size in pt (default: 10)

    Returns:
        QLabel styled as a badge
    """
    color, background = rating_colors(value)
    return Badge(f"{icon} {value}/10", color=color, background=background, font_size=font_size, weight="600")
