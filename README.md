# Leaf-Calc

Simple Flask web app to estimate leaf area from an uploaded photo.

## Features
- Enter measured length and width of the leaf.
- Upload an image of the leaf.
- Optional toggles for fenestrations and variegation.
- Returns leaf area and additional metrics such as area including/excluding fenestrations and percentage of variegation.
- Defaults to non-fenestrated, non-variegated leaves unless toggles are enabled.

## Usage
1. Install requirements: `pip install -r requirements.txt`
2. Run the app: `python app.py`
3. Open `http://localhost:5000` in a browser.
4. Fill in length and width, upload a leaf image, and submit.

The app assumes the leaf is photographed on a contrasting background.
