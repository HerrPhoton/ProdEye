from bs4 import BeautifulSoup
from icrawler import Parser


class GettyImagesParser(Parser):

    IMAGE_CLASS = "VxRXOwgHbHRi1LUtHYRl"

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        images = soup.find_all('img', class_=self.IMAGE_CLASS)
        for image in images:
            yield dict(file_url=image['src'])
