from sklearn.neighbors import KDTree
from io import BytesIO
from flask import Flask, request, make_response, jsonify
from PIL import Image
import os
import numpy as np
import base64
import requests

app = Flask(__name__)

response = requests.put('http://127.0.0.1:5000/registerReducer', data={"name": "mosaic-reducer", "url": "http://127.0.0.1:5010/reduceMosaic", "author": "Connor McGibbon"})

def mean_color(tile):
    return np.array(tile).mean(axis=(0, 1))

@app.route("/reduceMosaic", methods=["POST"])
def reduce():
    base_image = Image.open(request.files["baseImage"]).convert('RGB')
    mosaic1 = Image.open(request.files["mosaic1"]).convert('RGB')
    mosaic2 = Image.open(request.files["mosaic2"]).convert('RGB')

    rendered_tile_size = int(request.args.get("renderedTileSize"))
    tiles_across = int(request.args.get("tilesAcross"))
    file_format = request.args.get("fileFormat")

    base_width, base_height = base_image.size
    dim = base_width // tiles_across
    reduced_mosaic = Image.new('RGB', (tiles_across * rendered_tile_size, (base_height // dim) * rendered_tile_size))

    for x in range(tiles_across):
        for y in range(base_height // dim):
            base_tile = base_image.crop((x * dim, y * dim, (x + 1) * dim, (y + 1) * dim))
            mosaic1_tile = mosaic1.crop((x * rendered_tile_size, y * rendered_tile_size, (x + 1) * rendered_tile_size, (y + 1) * rendered_tile_size))
            mosaic2_tile = mosaic2.crop((x * rendered_tile_size, y * rendered_tile_size, (x + 1) * rendered_tile_size, (y + 1) * rendered_tile_size))

            base_tile_color = mean_color(base_tile)
            mosaic1_color_diff = np.linalg.norm(base_tile_color - mean_color(mosaic1_tile))
            mosaic2_color_diff = np.linalg.norm(base_tile_color - mean_color(mosaic2_tile))

            if mosaic1_color_diff < mosaic2_color_diff:
                reduced_mosaic.paste(mosaic1_tile, (x * rendered_tile_size, y * rendered_tile_size))
            else:
                reduced_mosaic.paste(mosaic2_tile, (x * rendered_tile_size, y * rendered_tile_size))

    buffer = BytesIO()
    reduced_mosaic.save(buffer, format=file_format)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers.set('Content-Type', f'image/{file_format.lower()}')
    response.headers.set('Content-Disposition', f'attachment; filename=reduced_mosaic.{file_format.lower()}')

    return response

if __name__ == "__main__":
    app.run(port=5010)
