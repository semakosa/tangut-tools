# The "Tangut Tool"

A standalone application for dynamic transcription and glossing of Tangut text.

## Overview

This tool allows you to work with Tangut text by:
- Viewing reconstructed pronunciations for each character using multiple systems
- Adding translations (glosses) for words or character groups
- Defining relationships between characters to form words
- Exporting your work in text format for use in documents

## Screenshot

![Tangut Tool Screenshot](screenshot.png)

*Screenshot of the "Tangut Tool" interface showing the main features.*

## Installation

### Prerequisites

The application requires GTK 4 and libadwaita:

```bash
# Ubuntu/Debian
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 libadwaita-1-dev

# Fedora
sudo dnf install python3-gobject gtk4 libadwaita-devel

# Arch Linux
sudo pacman -S python-gobject gtk4 libadwaita
```

### Running the application

Simply run:

```bash
python3 main.py
```

## Quick Start

1. **Enter Tangut text** in the input field (top of window)
2. Click **Convert** or press Enter
3. The characters appear in the editor with pronunciation and meaning options
4. Use the combo box to select meanings
5. Set relationships between characters:
   - `.` (dot): Characters form an unsegmented word
   - `-` (hyphen): Word with internal segmentation
   - ` ` (space): Separate words
6. Export your glossed text using Ctrl+E or the Export button

## Technical Architecture

The application consists of several main components:

- **main.py**: Application entry point and window management
- **glosser_tab.py**: Main content area with input, glossing, and output widgets
- **word_relation_widget.py**: Widget for editing word relationships and glosses
- **utils.py**: Utility functions and data model classes

## Data Sources

The application uses local data files:

- `data/20241129.tsv`: Pronunciation data for Tangut characters (very preliminary version!)
- `data/glossary.tsv`: Meanings for Tangut characters (dummy data for now)

## License

This software is released under the MIT License. The preliminary data files are provisionally provided under a Limited Public Use license, see [LICENSE-DATA.md](https://github.com/semakosa/tangut-tools/blob/main/LICENSE-DATA.md) for full details.