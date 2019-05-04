from flask import Flask, request
import configparser
from PIL import Image
import json
import os
import torch
import sys
from rockethub import Rocket

device_available = 'cuda' if torch.cuda.is_available() else 'cpu'

config = configparser.ConfigParser()
config.read('config.ini')
default_conf = config['DEFAULT']

DEVICE = default_conf.get('DEVICE', device_available)
ROCKET_URL = default_conf.get('ROCKET_URL', 'empty')
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

    out = model.postprocess(out_tensor, img)
    return json.dumps(str(out))


if __name__ == '__main__':
    if 'serve' in sys.argv:
        app.run(debug=False, host='0.0.0.0', port=PORT)


