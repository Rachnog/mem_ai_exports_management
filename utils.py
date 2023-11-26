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

class JSONProcessor:
    def __init__(self, json_data, vault_folder):
        self.json_data = json_data
        self.vault_folder = vault_folder

    def format_title_for_filename(self, title):
        # Replace problematic characters in the title for a valid filename
        return title.replace("/", "_").replace("\\", "_").replace(":", "_").replace("?", "_")

    def process_json(self):
        image_downloader = ImageDownloader(os.path.join(self.vault_folder, 'images'))
        markdown_processor = MarkdownProcessor()

        for item in tqdm(self.json_data, desc="Processing JSON Items"):
            markdown = item['markdown']
            title = item.get('title', 'Untitled')
            tags = ' '.join([f'#{tag}' for tag in item.get('tags', [])])
            created = item.get('created', 'Unknown creation date')
            updated = item.get('updated', 'Unknown update date')

            if markdown_processor.is_likely_misencoded_cyrillic(title):
                title = markdown_processor.fix_encoding(title)

            # Prepend tags, created, and updated info to markdown
            meta_info = f'Tags: {tags}\nCreated: {created}\nUpdated: {updated}\n\n'
            markdown = meta_info + markdown

            # Process images and update markdown
            image_urls = re.findall(r'!\[\]\((https://[^\)]+)\)', markdown)
            for image_url in image_urls:
                image_filename = image_downloader.download_image(image_url)
                if image_filename:
                    local_image_path = os.path.join('images', image_filename)
                    markdown = markdown.replace(image_url, local_image_path)

            if markdown_processor.is_likely_misencoded_cyrillic(markdown):
                markdown = markdown_processor.fix_encoding(markdown)

            markdown = re.sub(r'# (.+)', r'# \1\n', markdown)
            markdown = re.sub(r'- (.+)', r'* \1\n', markdown)
            markdown = markdown.strip() + '\n\n'

            formatted_title = self.format_title_for_filename(title)
            file_name = f'{self.vault_folder}/{formatted_title}.md'
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(markdown)

class JSONProcessorSubFolders:
    def __init__(self, json_data, vault_folder, copy_to_all_tags=False):
        self.json_data = json_data
        self.vault_folder = vault_folder
        self.copy_to_all_tags = copy_to_all_tags

    def format_title_for_filename(self, title):
        return title.replace("/", "_").replace("\\", "_").replace(":", "_").replace("?", "_")

    def process_json(self):
        markdown_processor = MarkdownProcessor()

        for item in tqdm(self.json_data, desc="Processing JSON Items"):
            original_markdown = item['markdown']
            title = item.get('title', 'Untitled')
            tags = item.get('tags', [])
            formatted_title = self.format_title_for_filename(title)

            if markdown_processor.is_likely_misencoded_cyrillic(title):
                title = markdown_processor.fix_encoding(title)

            tags_string = ' '.join([f'#{tag}' for tag in tags])  # Format tags for Markdown

            if not tags:
                tags = ['Untagged']  # Default folder for untagged notes

            for tag in tags:
                tag_folder = os.path.join(self.vault_folder, tag)
                images_folder = os.path.join(tag_folder, 'images')
                image_downloader = ImageDownloader(images_folder)

                if not os.path.exists(tag_folder):
                    os.makedirs(tag_folder)

                markdown = original_markdown
                # Insert tags after the title
                markdown = re.sub(r'(#[^\n]+\n)', r'\1' + tags_string + '\n\n', markdown, 1)

                # Process images and update markdown
                image_urls = re.findall(r'!\[\]\((https://[^\)]+)\)', markdown)
                for image_url in image_urls:
                    image_filename = image_downloader.download_image(image_url)
                    if image_filename:
                        local_image_path = os.path.join('images', image_filename)
                        markdown = markdown.replace(image_url, local_image_path)

                if markdown_processor.is_likely_misencoded_cyrillic(markdown):
                    markdown = markdown_processor.fix_encoding(markdown)

                file_path = os.path.join(tag_folder, f'{formatted_title}.md')
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(markdown)

                if not self.copy_to_all_tags:
                    break