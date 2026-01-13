"""
Script to download appropriate real estate images for apartments
"""
import os
import urllib.request
import ssl

# Create SSL context that doesn't verify certificates (for development)
ssl._create_default_https_context = ssl._create_unverified_context

# Image URLs from free stock photo sites (Unsplash/Pexels)
IMAGES = {
    'villa1.jpg': 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&q=80',  # Luxury villa
    'apartment1.jpg': 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&q=80',  # Modern apartment
    'studio1.jpg': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80',  # Studio apartment
    'duplex1.jpg': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80',  # Duplex/modern home
    'apartment2.jpg': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80',  # Investment apartment
}

def download_images():
    """Download all missing apartment images"""
    # Get the static images directory
    static_dir = os.path.join(os.path.dirname(__file__), 'app', 'static', 'images', 'apartments')
    os.makedirs(static_dir, exist_ok=True)
    
    print(f"Downloading images to: {static_dir}\n")
    
    for filename, url in IMAGES.items():
        filepath = os.path.join(static_dir, filename)
        
        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"✓ {filename} already exists, skipping...")
            continue
        
        try:
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filepath)
            print(f"✓ Successfully downloaded {filename}")
        except Exception as e:
            print(f"✗ Error downloading {filename}: {e}")
    
    print("\n✅ All images processed!")
    print(f"Images saved to: {static_dir}")

if __name__ == '__main__':
    download_images()
