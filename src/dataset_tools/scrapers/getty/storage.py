from ..base.storage import PrefixFileSystemStorage


class GettyImagesStorage(PrefixFileSystemStorage):

    def __init__(self, root_dir):
        super().__init__(root_dir, "getty_images_")
