from flask import Flask, request, send_file
import configparser
from PIL import Image
import json
import os
import torch
import sys
import io
from rocketbase import Rocket

device_available = 'cuda' if torch.cuda.is_available() else 'cpu'

config = configparser.ConfigParser()
config.read('config.ini')
default_conf = config['DEFAULT']

DEVICE = default_conf.get('DEVICE', device_available)
ROCKET_URL = default_conf.get('ROCKET_URL', 'empty')
ROCKET_FAMILY = default_conf.get('ROCKET_FAMILY', 'empty')
PORT = int(default_conf.get('PORT', 5042))
PORT = int(os.environ.get('PORT', PORT))

if device_available == 'cpu':
    DEVICE = 'cpu'

app = Flask(__name__)


def init_model():
    model = Rocket.land(ROCKET_URL).to(DEVICE)
    model.eval()
    return model


print('Starting application with following parameters:')
print(f'DEVICE: {DEVICE}')
print(f'ROCKET_URL: {ROCKET_URL}')
print(f'PORT: {PORT}')

model = init_model()


@app.route('/process', methods=['POST'])
def process():
    img_bytes = request.files.get('input')

    img = Image.open(img_bytes)
    img_tensor = model.preprocess(img).to(DEVICE)

    with torch.no_grad():
        out_tensor = model(img_tensor)

    if ROCKET_FAMILY in ['image_superresolution', 'image_style_transfer']:
        out = model.postprocess(out_tensor)
    else:
        out = model.postprocess(out_tensor, img)

    if type(out) == list:
        return json.dumps(str(out))
    elif "PIL" in str(type(out)):
        img_io = io.BytesIO()
        out.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(
            filename_or_fp=img_io,
            mimetype='image/png'
        )


if __name__ == '__main__':
    if 'serve' in sys.argv:
        app.run(debug=False, host='0.0.0.0', port=PORT)


