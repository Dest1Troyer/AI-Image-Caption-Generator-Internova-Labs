import os
import urllib.request
import time

def download_sample_images():
    print("==================================================")
    print("Downloading 10 Diverse Sample Images...")
    print("==================================================")
    
    samples_dir = "samples"
    os.makedirs(samples_dir, exist_ok=True)
    
    # We will use Lorem Picsum to download 10 random high-quality images.
    # We add a random parameter to force Picsum to return unique images.
    for i in range(1, 11):
        url = f"https://picsum.photos/800/600?random={i}"
        filename = f"sample_{i}.jpg"
        filepath = os.path.join(samples_dir, filename)
        
        print(f"Downloading image {i}/10 to {filepath}...")
        
        try:
            # Set a user-agent to prevent HTTP 403 Forbidden errors
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                out_file.write(response.read())
            # Sleep slightly to avoid spamming
            time.sleep(0.5)
        except Exception as e:
            print(f"Failed to download image {i}: {str(e)}")
            
    print("\n==================================================")
    print("Successfully Downloaded Sample Images!")
    print("==================================================")

if __name__ == "__main__":
    download_sample_images()
