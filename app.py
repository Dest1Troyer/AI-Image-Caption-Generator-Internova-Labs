import streamlit as st
import pandas as pd
from PIL import Image
import os
import io
import time
from model_helper import (
    generate_base_caption,
    get_style_variations,
    translate_caption,
    load_blip_model,
    LANGUAGES
)

# Set page configuration with a modern look
st.set_page_config(
    page_title="AI Image Caption Generator",
    page_icon="📸",
    layout="wide"
)

# Apply minimal, safe custom CSS to enhance typography and elements without breaking layouts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply clean font to headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Clean title styling */
    .app-title-container {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1.5rem;
    }
    
    .title-gradient {
        background: linear-gradient(135deg, #a78bfa 0%, #6366f1 50%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    
    .subtitle-text {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: 0.25rem;
    }

    /* Style code blocks (captions) with a colored left border */
    .stCodeBlock {
        border-left: 4px solid #6366f1 !important;
        border-radius: 6px !important;
        background-color: rgba(15, 23, 42, 0.4) !important;
    }
    
    /* Style translated code blocks with a blue left border */
    .translated-block .stCodeBlock {
        border-left: 4px solid #3b82f6 !important;
    }

    /* Sidebar info cards */
    .sidebar-card {
        padding: 1rem;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Centered Title and Subtitle
st.markdown("""
<div class="app-title-container">
    <span class="title-gradient">📸 AI Image Caption Generator</span>
    <p class="subtitle-text">Transform images into highly descriptive captions with style variations and translation.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar configurations
with st.sidebar:
    st.markdown("### ⚙️ Settings & Status")
    
    # Model Loading Status Info
    status_placeholder = st.empty()
    status_placeholder.info("⏳ Loading model weights...")
    
    try:
        processor, model, device = load_blip_model()
        status_placeholder.success(f"🟢 Model Ready ({device.upper()})")
    except Exception as e:
        status_placeholder.error("🔴 Model Load Error")
        st.error(f"Error details: {str(e)}")

    st.markdown("---")
    
    # Language Selector
    st.markdown("#### 🌐 Translation Settings")
    target_lang = st.selectbox(
        "Translate captions to:",
        options=list(LANGUAGES.keys()),
        index=1  # Default to Spanish
    )
    
    st.markdown("---")
    
    # Model details
    st.markdown("""
    <div class="sidebar-card">
        <h5 style="margin-top:0;">🤖 Model Details</h5>
        <p style="font-size:0.85rem; color:#94a3b8; line-height:1.4; margin-bottom:0;">
            Running <strong>Salesforce/blip-image-captioning-base</strong> locally. 
            No cloud APIs or subscription keys are required.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Tabs definition
tab1, tab2 = st.tabs(["🖼️ Single Image Captioner", "📁 Batch Processor"])

# Tab 1: Single Image Captioning
with tab1:
    col_left, col_right = st.columns([1, 1], gap="medium")
    
    with col_left:
        with st.container(border=True):
            st.markdown("### 📤 Upload Image")
            uploaded_file = st.file_uploader(
                "Upload a PNG, JPG, JPEG, or WEBP image:",
                type=["png", "jpg", "jpeg", "webp"],
                key="single_uploader"
            )
            
            # Simple, clean divider
            st.markdown("<p style='text-align: center; color: #475569; margin: 10px 0;'>- OR -</p>", unsafe_allow_html=True)
            use_sample = st.checkbox("🎯 Use sample demonstration image", value=False)
            
            image = None
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
            elif use_sample:
                sample_path = "samples/sample_1.jpg"
                if os.path.exists(sample_path):
                    image = Image.open(sample_path)
                else:
                    st.error("Sample image not found. Please upload an image.")
                    
            if image is not None:
                st.image(image, use_container_width=True, caption="Source Image")

    with col_right:
        with st.container(border=True):
            st.markdown("### 📝 Generated Descriptions")
            
            if image is not None:
                with st.spinner("Analyzing image and generating captions..."):
                    start_time = time.time()
                    base_caption = generate_base_caption(image)
                    inference_time = time.time() - start_time
                    
                    st.markdown(f"<p style='color: #64748b; font-size: 0.85rem;'>Inference completed in {inference_time:.2f} seconds.</p>", unsafe_allow_html=True)
                    
                    # Get the style variations
                    styles = get_style_variations(base_caption)
                    
                    # Render styling variations in nice containers
                    for style_name, caption_val in styles.items():
                        st.markdown(f"#### ✨ {style_name}")
                        st.code(caption_val, language="text")
                        
                        # Add translation if selected language is not English
                        if target_lang != "English":
                            translated_val = translate_caption(caption_val, target_lang)
                            st.markdown(f"<div class='translated-block' style='margin-left: 20px; margin-top: -10px; margin-bottom: 15px;'><p style='font-size:0.85rem; color:#3b82f6; margin-bottom:2px;'>🌐 {target_lang} Translation:</p>", unsafe_allow_html=True)
                            st.code(translated_val, language="text")
                            st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Please upload an image or enable the sample demonstration on the left to generate descriptions.")

# Tab 2: Batch Processing
with tab2:
    with st.container(border=True):
        st.markdown("### 📁 Batch Uploader")
        batch_files = st.file_uploader(
            "Select multiple images to process:",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="batch_uploader"
        )
        
    if batch_files:
        with st.container(border=True):
            st.markdown("### ⚙️ Batch Options")
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                batch_style = st.selectbox(
                    "Primary Style for Export:",
                    options=["Descriptive (Default)", "Professional/SEO", "Humorous", "Creative Story", "Alt-Text (Accessibility)"]
                )
            with col_opt2:
                include_trans = st.checkbox("Include translation in output file", value=True)
                
            run_batch = st.button("🚀 Process Batch Images")
            
        if run_batch:
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            gallery_container = st.container()
            
            for index, file in enumerate(batch_files):
                status_text.text(f"Processing image {index + 1} of {len(batch_files)}: {file.name}")
                
                # Load image
                img = Image.open(file)
                
                # Generate base caption
                base = generate_base_caption(img)
                all_styles = get_style_variations(base)
                selected_val = all_styles.get(batch_style, base)
                
                # Translate if requested
                trans_val = ""
                if include_trans and target_lang != "English":
                    trans_val = translate_caption(selected_val, target_lang)
                
                # Append to list
                results.append({
                    "Filename": file.name,
                    "Default Caption": base,
                    f"Selected Style ({batch_style})": selected_val,
                    f"Translation ({target_lang})": trans_val if trans_val else "N/A"
                })
                
                # Display dynamically in a clean row layout
                with gallery_container:
                    with st.container(border=True):
                        col_img, col_desc = st.columns([1, 3])
                        with col_img:
                            st.image(img, use_container_width=True)
                        with col_desc:
                            st.markdown(f"##### 📄 {file.name}")
                            st.markdown(f"**Default:** {base}")
                            st.markdown(f"**Selected Style ({batch_style}):**")
                            st.code(selected_val, language="text")
                            if trans_val:
                                st.markdown(f"**{target_lang} Translation:**")
                                st.code(trans_val, language="text")
                
                # Update progress
                progress_bar.progress((index + 1) / len(batch_files))
                
            status_text.success(f"Processed {len(batch_files)} images successfully!")
            
            # Export data
            df = pd.DataFrame(results)
            
            # CSV Download
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.markdown("### 📥 Export Compiled Results")
            st.download_button(
                label="📥 Download CSV File",
                data=csv_data,
                file_name="batch_captions.csv",
                mime="text/csv"
            )
            
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Upload multiple images in the section above to start batch processing.")
