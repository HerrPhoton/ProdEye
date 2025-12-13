from ..base.storage import PrefixFileSystemStorage


class GoogleStorage(PrefixFileSystemStorage):

    def __init__(self, root_dir):
        super().__init__(root_dir, "google_")
