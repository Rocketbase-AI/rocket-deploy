from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import configparser
import uvicorn, asyncio
from PIL import Image
from io import BytesIO
import sys
import json
import os
import torch

from rockethub import Rocket

device = 'cuda' if torch.cuda.is_available() else 'cpu'

config = configparser.ConfigParser()
config.read('config.ini')
default_conf = config['DEFAULT']

DEVICE = default_conf.get('DEVICE', device)
ROCKET_URL = default_conf.get('ROCKET_URL', 'empty')
PORT = int(default_conf.get('PORT', 5042))
PORT = int(os.environ.get('PORT', PORT))

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])


async def init_model():
    model = Rocket.land(ROCKET_URL).to(DEVICE)
    model.eval()
    return model

print('Starting application with following parameters:')
print(f'DEVICE: {DEVICE}')
print(f'ROCKET_URL: {ROCKET_URL}')
print(f'PORT: {PORT}')

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(init_model())]
model = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/process', methods=['POST'])
async def process(request):
    data = await request.form()
    img_bytes = await (data['input'].read())

    img = Image.open(BytesIO(img_bytes))
    img_tensor = model.preprocess(img).to(DEVICE)

    with torch.no_grad():
        out_tensor = model(img_tensor)

    out = model.postprocess(out_tensor, img)
    return JSONResponse(json.dumps(str(out)))

if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app=app, host='0.0.0.0', port=PORT)


