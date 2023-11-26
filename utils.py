import re
import requests
import time
import os
from tqdm import tqdm

class ImageDownloader:
    def __init__(self, images_folder):
        self.images_folder = images_folder
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)

    @staticmethod
    def get_file_extension(content_type):
        extension_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
        }
        return extension_map.get(content_type, '.jpg')

    def download_image(self, image_url):
        response = requests.head(image_url, allow_redirects=True)
        extension = self.get_file_extension(response.headers.get('content-type'))
        
        timestamp = int(time.time())
        counter = 0
        filename = f'image_{timestamp}_{counter}{extension}'
        save_path = os.path.join(self.images_folder, filename)

        while os.path.exists(save_path):
            counter += 1
            filename = f'image_{timestamp}_{counter}{extension}'
            save_path = os.path.join(self.images_folder, filename)
        
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return filename

        return None

class MarkdownProcessor:
    @staticmethod
    def fix_encoding(text):
        try:
            return text.encode('utf-8').decode('latin1').encode('latin1').decode('utf-8')
        except UnicodeError:
            return text

    @staticmethod
    def is_likely_misencoded_cyrillic(text):
        return "Ð" in text or "Ñ" in text

    def process_notes(self, notes, image_downloader):
        markdown_notes = []
        titles = []

        for note in tqdm(notes.split('---'), desc="Processing Notes"):
            if not note.strip():
                continue

            lines = note.strip().split('\n')
            title = lines[0].strip('# ').replace('/', '_').replace('\\', '_')
            if self.is_likely_misencoded_cyrillic(title):
                title = self.fix_encoding(title)
            titles.append(title)

            image_urls = re.findall(r'!\[\]\((https://[^\)]+)\)', note)
            for image_url in tqdm(image_urls, desc="Downloading Images", leave=False):
                image_filename = image_downloader.download_image(image_url)
                if image_filename:
                    local_image_path = os.path.join('images', image_filename)
                    note = note.replace(image_url, local_image_path)

            if self.is_likely_misencoded_cyrillic(note):
                note = self.fix_encoding(note)

            note = re.sub(r'# (.+)', r'# \1\n', note)
            note = re.sub(r'- (.+)', r'* \1\n', note)
            note = note.strip() + '\n\n'

            markdown_notes.append(note)

        return markdown_notes, titles