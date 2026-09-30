from Components.Badge import Badge

WORK_ARRANGEMENTS = ["Remote", "Hybrid", "On-site", "Unknown"]

# arrangement: (icon, text color, background, tooltip)
STYLES = {
    "Remote":  ("🏠", "#2e7d32", "#e8f5e9", "Fully remote"),
    "Hybrid":  ("🔀", "#1565c0", "#e3f2fd", "Hybrid (part remote, part in office)"),
    "On-site": ("🏢", "#ef6c00", "#fff3e0", "Fully on-site / in office"),
    "Unknown": ("❔", "#757575", "#f5f5f5", "Work arrangement not recorded"),
}


def normalize_work_arrangement(value):
    """
    Map whatever the AI (or an older record) stored to one of WORK_ARRANGEMENTS.

    e.g. "Fully Remote" -> "Remote", "onsite" / "In Office" -> "On-site", None -> "Unknown"
    """
    text = str(value or "").strip().lower()
    if "hybrid" in text:
        return "Hybrid"
    if "remote" in text:
        return "Remote"
    if any(word in text for word in ("on-site", "onsite", "on site", "in office", "in-office", "office")):
        return "On-site"
    return "Unknown"


def WorkArrangementBadge(value, font_size=10, show_text=True):
    """
    Create a badge showing whether a job is Remote / Hybrid / On-site (or Unknown)

    Args:
        value: Raw `Job['Work Arrangement']` value (normalized automatically)
        font_size: Font size in pt (default: 10)
        show_text: Show the label next to the icon; when False only the icon is shown (default: True)

    Returns:
        QLabel styled as a badge
    """
    arrangement = normalize_work_arrangement(value)
    icon, color, background, tooltip = STYLES[arrangement]
    text = f"{icon} {arrangement}" if show_text else icon
    return Badge(text, color=color, background=background, font_size=font_size, weight="600", tooltip=tooltip)
