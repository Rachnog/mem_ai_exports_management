import argparse
import json
import os
import re
import requests
import time
from tqdm import tqdm
from urllib.parse import urlparse, unquote

from utils import *

def main(json_file, vault_folder, copy_to_all_tags=False):
    with open(json_file, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    json_processor = JSONProcessorSubFolders(json_data, vault_folder, copy_to_all_tags)
    json_processor.process_json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON notes and download images into subfolders based on tags.")
    parser.add_argument("--json_file", default='./data/my_export.json', help="Path to the JSON file")
    parser.add_argument("--vault_folder", default='exports/my_export_json_subfolders', help="Path to the vault folder")
    parser.add_argument("--copy_to_all_tags", action='store_true', help="Copy notes to all tag folders")

    args = parser.parse_args()

    main(args.json_file, args.vault_folder, args.copy_to_all_tags)