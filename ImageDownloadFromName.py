from flask import Flask, request, jsonify
from icrawler.builtin import GoogleImageCrawler
import logging
import os
import time
import shutil

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Directory to store downloaded images
IMAGE_DIR = 'images1'


def download_images(search_query, index, max_images=1):
    try:
        # Create a temporary directory for download
        temp_dir = f'temp_{index}'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create an instance of GoogleImageCrawler
        crawler = GoogleImageCrawler(
            storage={'root_dir': temp_dir},
            feeder_threads=1,
            parser_threads=1,
            downloader_threads=1
        )
        
        # Download image
        crawler.crawl(
            keyword=search_query,
            max_num=max_images,
            min_size=(200,200),
            overwrite=True
        )
        
        # Move and rename the file from temp directory to images directory
        for filename in os.listdir(temp_dir):
            if os.path.isfile(os.path.join(temp_dir, filename)):
                # Get file extension
                ext = os.path.splitext(filename)[1]
                # Create new filename
                new_filename = f"{search_query.replace(' ', '_')}{ext}"
                # Move and rename file
                shutil.move(
                    os.path.join(temp_dir, filename),
                    os.path.join(IMAGE_DIR, new_filename)
                )
        
        # Remove temporary directory
        shutil.rmtree(temp_dir)
        
        logging.info(f"Successfully downloaded image for: {search_query}")
        
        # Add a small delay between requests
        time.sleep(2)
        
        return new_filename  # Returning the new filename for the image
    
    except Exception as e:
        logging.error(f"Failed to download image for {search_query}: {e}")
        # Clean up temp directory if it exists
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return None


@app.route('/download_image', methods=['POST'])
def download_image():
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        # Extract product name from the request
        product_name = data.get('product_name', '').strip()
        
        # Check if product name is provided
        if not product_name:
            return jsonify({"error": "Product name is required"}), 400
        
        # Create images directory if it doesn't exist
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)
        
        # Call the download_images function
        image_filename = download_images(product_name, 0, max_images=1)
        
        if image_filename:
            return jsonify({"message": f"Image downloaded successfully for {product_name}", "image_filename": image_filename}), 200
        else:
            return jsonify({"error": f"Failed to download image for {product_name}"}), 500
    
    except Exception as e:
        logging.error(f"Error in download_image endpoint: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(debug=True,port=5002)
