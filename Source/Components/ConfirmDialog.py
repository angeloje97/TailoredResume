from PySide6.QtWidgets import QMessageBox


def ConfirmDialog(title, text, informative_text="", icon=None, default_yes=False):
    """
    Show a blocking Yes/No confirmation box

    Args:
        title: Window title
        text: Main question text
        informative_text: Secondary text shown under the question (default: "")
        icon: QMessageBox.Icon, e.g. QMessageBox.Icon.Warning (default: None, no icon)
        default_yes: Whether Yes is the default button (default: False, No is default)

    Returns:
        True if the user clicked Yes
    """
    msg_box = QMessageBox()
    if icon is not None:
        msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    if informative_text:
        msg_box.setInformativeText(informative_text)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Yes if default_yes else QMessageBox.StandardButton.No)

    return msg_box.exec() == QMessageBox.StandardButton.Yes
