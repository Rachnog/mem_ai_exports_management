import argparse
import json
import os
import re
import requests
import time
from tqdm import tqdm
from urllib.parse import urlparse, unquote

from utils import *

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
