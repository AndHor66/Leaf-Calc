import io
from flask import Flask, request, render_template, jsonify
import numpy as np
import cv2

app = Flask(__name__)


def process_image(file_stream, length, width, fenestrated=False, variegated=False):
    file_bytes = np.asarray(bytearray(file_stream.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image")

    # Convert to grayscale and create mask
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = cv2.bitwise_not(mask)  # assume leaf darker than background

    # Clean up mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Bounding box for scaling
    coords = cv2.findNonZero(mask)
    x, y, w, h = cv2.boundingRect(coords)
    pixel_area = (length / h) * (width / w)

    leaf_area_px = cv2.countNonZero(mask)
    leaf_area = leaf_area_px * pixel_area

    result = {"leaf_area": leaf_area}

    if fenestrated:
        # Fill holes to get area including fenestrations
        flood = mask.copy()
        h_, w_ = mask.shape
        flood_mask = np.zeros((h_ + 2, w_ + 2), np.uint8)
        cv2.floodFill(flood, flood_mask, (0, 0), 255)
        flood_inv = cv2.bitwise_not(flood)
        filled_mask = mask | flood_inv
        leaf_with_holes_px = cv2.countNonZero(filled_mask)
        leaf_with_holes = leaf_with_holes_px * pixel_area
        result["leaf_area_including_fenestrations"] = leaf_with_holes
        result["leaf_area_excluding_fenestrations"] = leaf_area

    if variegated:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # low saturation considered variegated
        var_mask = (hsv[:, :, 1] < 50).astype(np.uint8) * 255
        var_mask = cv2.bitwise_and(var_mask, mask)
        var_area_px = cv2.countNonZero(var_mask)
        var_area = var_area_px * pixel_area
        result["variegated_area"] = var_area
        result["variegation_percent"] = (var_area / leaf_area) * 100 if leaf_area else 0

    return result


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        length = float(request.form['length'])
        width = float(request.form['width'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid length or width'}), 400

    fenestrated = 'fenestrated' in request.form
    variegated = 'variegated' in request.form
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'Image required'}), 400

    try:
        result = process_image(file.stream, length, width, fenestrated, variegated)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
