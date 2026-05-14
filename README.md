# Business Card Image Generator

[![Business Card Image Generator logo](docs/logo.svg)](docs/logo.svg)

[![Python CI](https://github.com/Boxgui12/business-card-image-generator/actions/workflows/python-ci.yml/badge.svg)](https://github.com/Boxgui12/business-card-image-generator/actions/workflows/python-ci.yml)

Business card generator in Python with Pillow and Flask.

## Project Structure

- `backend/`: image generation logic and Flask server
- `frontend/`: HTML templates and Bootstrap/CSS styling
- `.venv/`: local virtual environment

## Requirements

- Python 3.10+ recommended
- Dependencies installed in the virtual environment

## Installation

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Quick Start

1. Activate the virtual environment.
2. Run the server with `.\.venv\Scripts\python app.py`.
3. Open `http://127.0.0.1:5000`.
4. Fill in the form, choose a category, and generate the 10 designs.
5. Select the final design and download the PNG.

## Run the Server

```powershell
.\.venv\Scripts\python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Run the CLI Version

```powershell
.\.venv\Scripts\python business_card_generator.py --lang en
```

## Visual Examples

### Business Card Preview

![Business card example modern](docs/example-card-modern.png)

### Another Generated Style

![Business card example classic](docs/example-card-classic.png)

## Notes

- The interface supports English and Spanish.
- You can attach a photo to frame inside the card.
- The web flow generates 10 random designs and then lets you choose one before creating the final card.
- Before generating the gallery, you can choose a style category and only designs from that category will be shown.
- The gallery includes style filters to browse classic, modern, and dark designs.
- The selector and main button take on the accent color of the chosen category.
- Generated cards are saved in `backend/generated_cards/`.
