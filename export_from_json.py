import argparse
import json
import os
import re
import requests
import time
from tqdm import tqdm
from urllib.parse import urlparse, unquote

from utils import *

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

def main(json_file, vault_folder):
    with open(json_file, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    json_processor = JSONProcessor(json_data, vault_folder)
    json_processor.process_json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON notes and download images.")
    parser.add_argument("--json_file", default='./data/my_export.json', help="Path to the JSON file")
    parser.add_argument("--vault_folder", default='exports/my_export_json', help="Path to the vault folder")

    args = parser.parse_args()

    main(args.json_file, args.vault_folder)
