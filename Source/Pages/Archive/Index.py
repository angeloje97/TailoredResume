import os
from PySide6.QtWidgets import QMessageBox
from Utility import paths
from Components.ArchiveItem import ArchiveItem
from Components.PagedListPage import PagedListPage
from Components.ConfirmDialog import ConfirmDialog


class ArchivePage(PagedListPage):
    """Archive page listing applications moved out of History (manually or by auto-archive)."""

    def __init__(self, stacked_widget):
        super().__init__(stacked_widget, "Archive", include_favorites=False, include_saved=False,
                         list_spacing=12, list_margins=(0, 15, 0, 20), list_background="#f5f5f5")

    def load_datas(self):
        from Utility import get_archived_datas
        return get_archived_datas()

    def create_item(self, data):
        return ArchiveItem(data, on_restore=self.restore_archive_item, on_delete=self.delete_archive_item)

    def restore_archive_item(self, data):
        """Restore an archived item back to the history section"""
        from Utility import restore_archive_data

        file_name = f"{data['Meta']['File Name']}"

        if ConfirmDialog("Restore Archive", f"Restore '{file_name}' back to history?", default_yes=True):
            # Restore the JSON file
            restore_archive_data(file_name)

            # Refresh the archive page
            self.reload()

    def delete_archive_item(self, data):
        """Delete an archived item permanently"""
        file_name = f"{data['Meta']['File Name']}"

        if ConfirmDialog("Delete Archived Item", "Are you sure you want to permanently delete this item?",
                         f"{file_name}\n\nThis action cannot be undone.", icon=QMessageBox.Icon.Warning):
            # Delete the JSON file from archive folder
            archived_path = paths['json_data'] / 'Archived'
            json_file_path = archived_path / f"{file_name}.json"
            if json_file_path.exists():
                os.remove(json_file_path)
                print(f"Deleted archived item: {file_name}")

            # Refresh the archive page
            self.reload()
