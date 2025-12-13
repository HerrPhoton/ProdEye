from ..base.storage import PrefixFileSystemStorage


class BingStorage(PrefixFileSystemStorage):

    def __init__(self, root_dir):
        super().__init__(root_dir, "bing_")
