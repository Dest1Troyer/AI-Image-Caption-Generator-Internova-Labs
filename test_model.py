import time
from PIL import Image
from model_helper import generate_base_caption, get_style_variations, translate_caption

def main():
    print("==================================================")
    print("Testing Model Loading and Caption Generation...")
    print("==================================================")
    
    # 1. Load image
    image_path = "sample.jpg"
    print(f"Loading image from {image_path}...")
    try:
        image = Image.open(image_path)
        print("Image loaded successfully.")
    except Exception as e:
        print(f"Error loading image: {str(e)}")
        return
        
    # 2. Run inference
    print("\nLoading model and running caption generation (this will download model on first run)...")
    start_time = time.time()
    try:
        base_caption = generate_base_caption(image)
        duration = time.time() - start_time
        print(f"Base Caption generated in {duration:.2f} seconds:")
        print(f"  >>> '{base_caption}'")
    except Exception as e:
        print(f"Error during caption generation: {str(e)}")
        return
        
    # 3. Generate style variations
    print("\nGenerating caption style variations...")
    styles = get_style_variations(base_caption)
    for style_name, caption in styles.items():
        print(f"  [{style_name}]: {caption}")
        
    # 4. Test translation
    print("\nTesting translation to Spanish (Español)...")
    try:
        spanish_caption = translate_caption(base_caption, "Spanish (Español)")
        print(f"  >>> '{spanish_caption}'")
    except Exception as e:
        print(f"Translation error: {str(e)}")

    print("\n==================================================")
    print("Test Completed Successfully!")
    print("==================================================")

if __name__ == "__main__":
    main()
