from icrawler import ImageDownloader


class PrefixDownloader(ImageDownloader):

    def get_filename(self, task, default_ext):
        downloader = super()
        filename = downloader.get_filename(task, default_ext)
        return self.storage.prefix + filename
