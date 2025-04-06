from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import io
import json
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_bytes, settings):
    try:
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")

        logger.info(f"Processing image with settings: {settings}")

        # 1. Kirpma islemi
        if settings.get('cropEnabled', False) and 'crop' in settings:
            crop = settings['crop']
            if all(key in crop for key in ['x', 'y', 'width', 'height']):
                x = int(crop['x'])
                y = int(crop['y'])
                w = int(crop['width'])
                h = int(crop['height'])
                
                # Sınır kontrolleri
                img_h, img_w = img.shape[:2]
                x = max(0, min(x, img_w - 1))
                y = max(0, min(y, img_h - 1))
                w = max(1, min(w, img_w - x))
                h = max(1, min(h, img_h - y))
                
                img = img[y:y+h, x:x+w]

        # 2. Boyutlandırma
        if 'width' in settings and 'height' in settings:
            width = int(settings['width'])
            height = int(settings['height'])
            if width > 0 and height > 0:
                interpolation = cv2.INTER_AREA if (width < img.shape[1] or height < img.shape[0]) else cv2.INTER_CUBIC
                img = cv2.resize(img, (width, height), interpolation=interpolation)

        # 3. Döndürme
        if 'rotation' in settings:
            angle = float(settings['rotation'])
            if angle in [90, 180, 270]:
                if angle == 90:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                elif angle == 180:
                    img = cv2.rotate(img, cv2.ROTATE_180)
                elif angle == 270:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            else:
                h, w = img.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                
                # Yeni boyutları hesapla (resmin kesilmemesi için)
                cos = np.abs(M[0, 0])
                sin = np.abs(M[0, 1])
                new_w = int((h * sin) + (w * cos))
                new_h = int((h * cos) + (w * sin))
                
                # Döndürme matrisini güncelle
                M[0, 2] += (new_w / 2) - center[0]
                M[1, 2] += (new_h / 2) - center[1]
                
                # Yeni boyutlarda beyaz arka planlı bir görüntü oluştur
                rotated_img = cv2.warpAffine(
                    img, M, (new_w, new_h),
                    flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT,
                    borderValue=(255, 255, 255)  # Beyaz arkaplan
                )
                
                # Orjinal görüntüyü güncelle
                img = rotated_img

        # 4. Flip
        if 'flip' in settings:
            flip_mode = settings['flip']
            if flip_mode == 'horizontal':
                img = cv2.flip(img, 1)
            elif flip_mode == 'vertical':
                img = cv2.flip(img, 0)
            elif flip_mode == 'both':
                img = cv2.flip(img, -1)

        # RGB2'ye dönüştürme
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        raise

@app.route('/process-image', methods=['POST'])
def process_image_route():
    try:
        # Dosyayı doğrula
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Parse settings
        settings = request.form.get('settings')
        if not settings:
            return jsonify({'error': 'No settings provided'}), 400
        
        settings = json.loads(settings)
        
        # Resmi isle
        processed_img = process_image(file.read(), settings)
        
        # Encode to PNG
        success, buffer = cv2.imencode('.png', cv2.cvtColor(processed_img, cv2.COLOR_RGB2BGR))
        if not success:
            return jsonify({'error': 'Failed to encode image'}), 500
        
        # Create response
        img_io = io.BytesIO(buffer.tobytes())
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name='processed.png'
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)