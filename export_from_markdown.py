import argparse
import os
from tqdm import tqdm
from urllib.parse import urlparse, unquote

from utils import *

def save_markdown_files(markdown_notes, titles, vault_folder):
    for note, title in tqdm(zip(markdown_notes, titles), total=len(markdown_notes), desc="Saving Markdown Files"):
        file_name = f'{vault_folder}/{title}.md'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(note)

def main(markdown_file, vault_folder):
    with open(markdown_file, 'r', encoding='utf-8') as file:
        notes = file.read()

    image_downloader = ImageDownloader(os.path.join(vault_folder, 'images'))
    markdown_processor = MarkdownProcessor()
    markdown_notes, titles = markdown_processor.process_notes(notes, image_downloader)
    save_markdown_files(markdown_notes, titles, vault_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process markdown notes and download images.")
    parser.add_argument("--markdown_file", default='./data/my_export.md', help="Path to the markdown file")
    parser.add_argument("--vault_folder", default='exports/my_export_md', help="Path to the vault folder")

    args = parser.parse_args()

    main(args.markdown_file, args.vault_folder)