# Mem.ai exports management

This repository contains Python scripts for processing exported notes in both Markdown (MD) and JSON formats. The scripts are designed to handle note data, download associated images, and generate Markdown files with updated image paths and additional metadata.

## Contents

- `process_md.py`: Script to process Markdown files, download images, and create new Markdown files with local image paths.
- `process_json.py`: Script to process JSON exports of notes, download images, and create Markdown files with metadata such as tags and timestamps.
- `data/`: Directory for storing your input MD or JSON files.
- `exports/`: Directory where processed Markdown files and downloaded images will be saved.

## Prerequisites

Before running the scripts, ensure you have Python installed on your system. The scripts require the following Python libraries:
- `requests`
- `tqdm`

## Usage

### Processing Markdown Files

To process an MD file, place your MD file in the `data/` directory and run the `process_md.py` script. By default, the script looks for `./data/my_export.md` and saves processed files in the `exports/my_export` directory.

Command to run the script:

```python process_md.py --markdown_file ./data/my_export.md --vault_folder exports/my_export```

### Processing JSON Files

To process a JSON file, place your JSON file in the `data/` directory and run the `process_json.py` script. The default JSON file path is `./data/my_export.json`, and the processed files are saved in the `exports/my_export` directory.

Command to run the script:

```python process_json.py --json_file ./data/my_export.json --vault_folder exports/my_export```

Both scripts will create Markdown files with any linked images downloaded and stored in the `exports/my_export/images` directory. Image paths in the Markdown files will be updated to reference these local images.

## Contributing

Contributions to improve these scripts are welcome. Please feel free to fork this repository and submit pull requests with your improvements.



