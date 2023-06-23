from sklearn.neighbors import KDTree
from io import BytesIO
from flask import Flask, request, make_response, jsonify
from PIL import Image
import os
import numpy as np
import base64
import requests

app = Flask(__name__)

tile_images_dir = "../../MMGs/fish/tile_images_fish/"
tile_image_count = len(os.listdir(tile_images_dir))

response = requests.put('http://127.0.0.1:5000/addMMG', data={"name": "fish-mmg", "url": "http://127.0.0.1:5006/makeMosaic/", "author": "Connor McGibbon", "tileImageCount": tile_image_count})

images = []
colors = []

for file in os.listdir(tile_images_dir):
    tile = Image.open(f'{tile_images_dir}/{file}').convert('RGB').resize((50, 50))
    images.append(tile)
    colors.append(np.array(tile).mean(axis=(0, 1)))

kd_tree = KDTree(colors)

def make_mosaic(img_data, tiles_across, rendered_tile_size):
    base_image = img_data
    base_width, base_height = base_image.size
    dim = base_width // tiles_across
    mosaic = Image.new('RGB', (tiles_across * rendered_tile_size, (base_height // dim) * rendered_tile_size))

    for x in range(tiles_across):
        for y in range(base_height // dim):
            current_tile = base_image.crop((x * dim, y * dim, (x + 1) * dim, (y + 1) * dim))
            color = np.array(current_tile).mean(axis=(0, 1))
            _, index = kd_tree.query([color])
            resized_tile = images[index[0][0]].resize((rendered_tile_size, rendered_tile_size))
            mosaic.paste(resized_tile, (x * rendered_tile_size, y * rendered_tile_size))

    buffer = BytesIO()
    mosaic.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue())
    return b64

@app.route('/makeMosaic/', methods=["POST"])
def POST_generateMosaic():
    img_data = request.files["image"].read()
    img = Image.open(BytesIO(img_data)).convert('RGB')

    tiles_across = int(request.args.get("tilesAcross"))
    rendered_tile_size = int(request.args.get("renderedTileSize"))
    file_format = request.args.get("fileFormat")

    b64_mosaic = make_mosaic(img, tiles_across, rendered_tile_size)
    mosaic = Image.open(BytesIO(base64.b64decode(b64_mosaic)))

    buffer = BytesIO()
    mosaic.save(buffer, format=file_format)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers.set('Content-Type', f'image/{file_format.lower()}')
    response.headers.set('Content-Disposition', f'attachment; filename=mosaic.{file_format.lower()}')

    return response


if __name__ == "__main__":
    app.run(port=5006)