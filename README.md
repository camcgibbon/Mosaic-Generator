## High-level overview

The system is designed to generate mosaic images using a microservice architecture. The system consists of three main components:

1. Middleware (app.py): The main Flask application that serves as the user-facing frontend and communicates with the Microservice Mosaic Generators (MMGs).
2. Frontend (index.html, 1989.js) The webpage that provides the user with a simple and understandable interface
3. Mosaic Generators (MMGs/abstract_art,fish,naruto,smash_bros,vaporwave): Standalone MMG's that generate mosaics using different themed tile images.

## MMG connection to the middleware

The MMGs are connected to the middleware through predefined URLs in the middleware's 'mmg_urls' list:

mmg_urls = [
    'http://localhost:5001',
    'http://localhost:5002',
    'http://localhost:5003',
    'http://localhost:5004',
    'http://localhost:5005'
]

When an MMG is launched, it starts listening on its corresponding port. The middleware sends requests to the MMGs using these URLs. To add a new MMG, you would need to add its URL to the mmg_urls list manually.

## Middleware request packet
When a user uploads a base image, the middleware sends a POST request to each MMG to generate a mosaic. The following route is used for this request:

- Route: /generateMosaic
- HTTP Verb: POST
- Required Parameters:
    1. image (file): The base image to be used for generating the mosaic.
    2. tiles_across (integer): The number of horizontal tiles in the final mosaic.
    3. rendered_tile_size (integer): The size (in pixels) of each tile in the final mosaic image.

## Additional details/advanced features

- The system saves generated mosaics to a "generated_images" directory in the middleware application. This allows serving the images without relying on data URLs, reducing the size of the JSON response and improving performance.

- The system uses UUIDs to uniquely name the generated mosaic images, ensuring that multiple users can use the application simultaneously without overwriting each other's images.