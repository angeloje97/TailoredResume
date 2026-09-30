import html
import re
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


# A rubric item starts a line or a new sentence: "Tech stack overlap (~2.7/3): ..." or "Overall: ..."
_ITEM_START = re.compile(
    r"(?:^|(?<=[.!?] )|(?<=[.!?]['\"”’)] ))"
    r"(?:(?P<name>[A-Z][A-Za-z/&'’\- ]{1,40}?) \((?P<score>[^()\n]{1,40})\):|(?P<overall>Overall)[,:])\s*",
    re.MULTILINE,
)


def parse_rating_description(text):
    """Split a rating description into [(name, score, body)] rubric items. name/score are None for plain prose."""
    text = re.sub(r"[ \t]*\n\s*", "\n", (text or "").strip())
    if not text:
        return []

    matches = list(_ITEM_START.finditer(text))
    if not matches:
        return [(None, None, paragraph) for paragraph in text.split("\n") if paragraph.strip()]

    items = []
    intro = text[:matches[0].start()].strip()
    if intro:
        items.append((None, None, intro))

    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        if match.group('overall'):
            items.append(("Overall", None, body[:1].upper() + body[1:]))
        else:
            items.append((match.group('name').strip(), match.group('score').strip(), body))
    return items


def _score_color(score):
    """Green for positive points, red for negative, gray for neutral/qualitative scores"""
    stripped = score.lstrip("~ ")
    if stripped.startswith(("-", "−")):
        return "#c62828", "#fdecea"
    if stripped.startswith("+") or stripped[:1].isdigit():
        return "#2e7d32", "#e8f5e9"
    return "#616161", "#f0f0f0"


class RatingBreakdown(QWidget):
    """Readable, itemized view of an AI rating description (one block per rubric item)."""

    def __init__(self, description, font_size=11):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        for name, score, body in parse_rating_description(description):
            parts = []
            if name:
                heading = f"<b style='color:#222;'>{html.escape(name)}</b>"
                if score:
                    color, background = _score_color(score)
                    heading += (f"&nbsp;&nbsp;<span style='color:{color}; background-color:{background};'>"
                                f"&nbsp;{html.escape(score)}&nbsp;</span>")
                parts.append(heading)
            if body:
                parts.append(f"<span style='color:#444;'>{html.escape(body)}</span>")

            label = QLabel("<br>".join(parts))
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setStyleSheet(f"font-size: {font_size}pt; padding-left: 8px;")
            layout.addWidget(label)
