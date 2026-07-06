import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import streamlit as st
import random
from deep_translator import GoogleTranslator

# Map languages to their codes
LANGUAGES = {
    "English": "en",
    "Spanish (Español)": "es",
    "French (Français)": "fr",
    "German (Deutsch)": "de",
    "Japanese (日本語)": "ja",
    "Hindi (हिन्दी)": "hi"
}

@st.cache_resource
def load_blip_model():
    """
    Load and cache the BLIP processor and model.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # We use Salesforce/blip-image-captioning-base which is lightweight and accurate
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    return processor, model, device

def generate_base_caption(image, max_new_tokens=50):
    """
    Generate the base descriptive caption for the image using BLIP.
    """
    processor, model, device = load_blip_model()
    
    # Ensure image is in RGB mode
    if image.mode != "RGB":
        image = image.convert("RGB")
        
    inputs = processor(images=image, return_tensors="pt").to(device)
    
    # Generate caption using beam search
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, num_beams=5, early_stopping=True)
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    
    # Capitalize the first letter
    if caption:
        caption = caption[0].upper() + caption[1:]
    return caption

def get_style_variations(base_caption):
    """
    Generates variations of the caption for different styles.
    """
    if not base_caption:
        return {}
        
    # Standardize string capitalization
    caption_lower = base_caption.lower()
    if caption_lower.startswith("a ") or caption_lower.startswith("an "):
        content = caption_lower
    else:
        content = f"a {caption_lower}"
        
    # Professional/SEO style: Rich descriptors, hashtags, marketing focus
    seo_templates = [
        f"A striking professional photograph capturing {content}. Ideal for commercial marketing, design portfolios, and creative editorial projects. #visualart #photography #branding #creativeconcept",
        f"Stunning high-resolution capture showcasing {content}. A perfect asset for digital content creators and brand storytelling. #digitalmarketing #editorial #stockphotography #aesthetics",
        f"Professional shot of {content}, highlighted by natural lighting and crisp details. Tailored for modern web layouts and social media feeds. #contentcreation #designinspiration #stockimages #proshot"
    ]
    seo_caption = random.choice(seo_templates)
    
    # Humorous style: Quirky commentary on the image content
    humorous_templates = [
        f"Plot twist: It's actually just {content} trying to look dramatic for the camera.",
        f"That moment when you realize you're looking at {content} and it's looking right back at you. Awkward.",
        f"Legend has it that {content} is still waiting for its coffee to kick in.",
        f"100% natural, organic {content}. Warning: may cause sudden bursts of visual satisfaction.",
        f"Just {content} doing its absolute best today. Please show some appreciation."
    ]
    humorous_caption = random.choice(humorous_templates)
    
    # Creative Story: An artistic narrative hook
    creative_templates = [
        f"In the quiet stillness of the afternoon, {content} emerged as a silent witness to the passage of time...",
        f"A canvas of reality: {content}, painted by the subtle strokes of light and shadow.",
        f"Whispers of the modern world, beautifully embodied in {content}. A story waiting to be told.",
        f"Captured in a single frame, {content} tells a tale of design, purpose, and visual poetry."
    ]
    creative_caption = random.choice(creative_templates)
    
    # Accessibility Alt-Text: Clear, objective, screen-reader friendly
    alt_text = f"Close-up photograph displaying {content}, focused on textures and composition."
    
    return {
        "Descriptive (Default)": base_caption,
        "Professional/SEO": seo_caption,
        "Humorous": humorous_caption,
        "Creative Story": creative_caption,
        "Alt-Text (Accessibility)": alt_text
    }

def translate_caption(text, target_lang_name):
    """
    Translates the given text into the target language.
    """
    target_code = LANGUAGES.get(target_lang_name, "en")
    if target_code == "en":
        return text
        
    try:
        translator = GoogleTranslator(source='auto', target=target_code)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        return f"[Translation Error: {str(e)}]"
