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

# Set page configuration
st.set_page_config(
    page_title="AI Image Caption Generator",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS for premium styling
st.markdown("""
<style>
    /* Main container and font styling */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0b0f17;
        font-family: 'Outfit', sans-serif;
        color: #e2e8f0;
    }
    
    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Header layout */
    .header-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        background: radial-gradient(circle at top, rgba(124, 58, 237, 0.1) 0%, rgba(11, 15, 23, 0) 70%);
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(124, 58, 237, 0.05);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #a78bfa 0%, #6366f1 50%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 2px 10px rgba(124, 58, 237, 0.15));
    }
    
    .subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        font-weight: 300;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Styled container cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(124, 58, 237, 0.3);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.25);
        gap: 6px;
    }
    
    .status-dot {
        height: 8px;
        width: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #10b981;
    }
    
    /* Streamlit widgets overrides */
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.65rem 1.75rem;
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.25s ease;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.25);
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 22px rgba(124, 58, 237, 0.4);
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        border-color: rgba(255, 255, 255, 0.2);
        color: #ffffff;
    }
    
    div.stButton > button:active {
        transform: translateY(1px);
    }
    
    /* Caption box rendering */
    .caption-container {
        background: rgba(15, 23, 42, 0.65);
        border-left: 4px solid #7c3aed;
        padding: 1.25rem;
        border-radius: 0 12px 12px 0;
        margin: 1.25rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.03);
        border-right: 1px solid rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }
    
    .caption-type {
        font-size: 0.85rem;
        font-weight: 700;
        color: #c084fc;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.35rem;
    }
    
    .caption-content {
        font-size: 1.2rem;
        color: #f8fafc;
        font-weight: 400;
        line-height: 1.6;
    }
    
    /* Section dividers */
    .glow-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(124, 58, 237, 0) 0%, rgba(124, 58, 237, 0.3) 50%, rgba(124, 58, 237, 0) 100%);
        margin: 2rem 0;
    }
    
    /* Tab formatting */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(15, 23, 42, 0.4);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
        color: #94a3b8;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #f1f5f9;
        background-color: rgba(255, 255, 255, 0.03);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(124, 58, 237, 0.15) !important;
        color: #a78bfa !important;
        border-bottom: 2px solid #7c3aed !important;
    }
    
    /* Batch grid item */
    .batch-item {
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        background: rgba(15, 23, 42, 0.3);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to generate custom copy button html
def custom_copy_button(text_id, text_to_copy):
    escaped_text = text_to_copy.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    html_code = f"""
    <div style="text-align: right; margin-top: -5px;">
        <button id="copy-btn-{text_id}" style="
            background: rgba(124, 58, 237, 0.15);
            border: 1px solid rgba(124, 58, 237, 0.3);
            color: #d8b4fe;
            padding: 5px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.8rem;
            transition: all 0.2s ease;
            font-family: inherit;
        " onclick="
            const textarea = document.createElement('textarea');
            textarea.value = '{escaped_text}';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            
            const btn = document.getElementById('copy-btn-{text_id}');
            btn.innerHTML = '✓ Copied!';
            btn.style.background = 'rgba(16, 185, 129, 0.2)';
            btn.style.color = '#34d399';
            btn.style.borderColor = 'rgba(16, 185, 129, 0.4)';
            
            setTimeout(() => {{
                btn.innerHTML = 'Copy Caption';
                btn.style.background = 'rgba(124, 58, 237, 0.15)';
                btn.style.color = '#d8b4fe';
                btn.style.borderColor = 'rgba(124, 58, 237, 0.3)';
            }}, 2000);
        ">Copy Caption</button>
    </div>
    """
    return html_code

# Header
st.markdown("""
<div class="header-container">
    <div class="main-title">📸 AI Image Caption Generator</div>
    <div class="subtitle">Upload your images and automatically generate beautiful, descriptive captions with multiple style variations and multilingual support using HuggingFace BLIP.</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings & Info")
    
    # Model Loading Status Info
    status_placeholder = st.empty()
    status_placeholder.markdown("""
    <div class="status-badge" style="background-color: rgba(245, 158, 11, 0.1); color: #f59e0b; border-color: rgba(245, 158, 11, 0.25);">
        <span class="status-dot" style="background-color: #f59e0b; box-shadow: 0 0 8px #f59e0b;"></span>
        Model Loading...
    </div>
    """, unsafe_allow_html=True)
    
    try:
        processor, model, device = load_blip_model()
        status_placeholder.markdown(f"""
        <div class="status-badge">
            <span class="status-dot"></span>
            Model Ready ({device.upper()})
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        status_placeholder.markdown(f"""
        <div class="status-badge" style="background-color: rgba(239, 68, 68, 0.1); color: #ef4444; border-color: rgba(239, 68, 68, 0.25);">
            <span class="status-dot" style="background-color: #ef4444; box-shadow: 0 0 8px #ef4444;"></span>
            Load Error
        </div>
        """, unsafe_allow_html=True)
        st.error(f"Failed to load model: {str(e)}")

    st.markdown("---")
    st.markdown("### 🌐 Translation Settings")
    target_lang = st.selectbox(
        "Select Target Language for translation:",
        options=list(LANGUAGES.keys()),
        index=1  # Default to Spanish
    )
    
    st.markdown("---")
    st.markdown("### 🤖 About the Model")
    st.markdown("""
    This app runs the **Salesforce/blip-image-captioning-base** model locally. It uses a ViT (Vision Transformer) backbone and a BERT-like language model to generate highly accurate descriptions of images.
    
    **Features:**
    - Fast local inference.
    - Zero cloud API dependency.
    - Automatic device optimization (uses CUDA if available).
    """)

# Create Tabs
tab1, tab2 = st.tabs(["🖼️ Single Image Captioning", "📁 Batch Image Processing"])

# Tab 1: Single Image Captioning
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Drag and drop your image here or browse",
            type=["png", "jpg", "jpeg", "webp"],
            key="single_uploader"
        )
        
        # Test Sample option
        st.markdown("<p style='text-align: center; color: #94a3b8; margin: 10px 0;'>- OR -</p>", unsafe_allow_html=True)
        use_sample = st.checkbox("🎯 Use sample image")
        
        image = None
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
        elif use_sample:
            sample_path = "samples/sample_1.jpg"
            if os.path.exists(sample_path):
                image = Image.open(sample_path)
            else:
                st.info("Sample image 'samples/sample_1.jpg' not found. Please upload an image.")
                # We show info if sample doesn't exist yet, but we will make sure it is generated.
                
        if image is not None:
            st.image(image, use_column_width=True, caption="Uploaded Image")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📝 Generated Captions")
        
        if image is not None:
            with st.spinner("Analyzing image and generating captions..."):
                start_time = time.time()
                base_caption = generate_base_caption(image)
                inference_time = time.time() - start_time
                
                # Get styling variations
                styles = get_style_variations(base_caption)
                
                st.markdown(f"<p style='color: #64748b; font-size: 0.85rem;'>Inference took {inference_time:.2f} seconds</p>", unsafe_allow_html=True)
                
                # Render styles in interactive expanders
                for idx, (style_name, style_val) in enumerate(styles.items()):
                    with st.expander(f"✨ {style_name}", expanded=(idx == 0)):
                        # Style text container
                        st.markdown(f"""
                        <div class="caption-container">
                            <div class="caption-type">{style_name}</div>
                            <div class="caption-content">{style_val}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Copy button
                        st.components.v1.html(custom_copy_button(f"style_{idx}", style_val), height=35)
                        
                        # Translation section
                        if target_lang != "English":
                            with st.spinner("Translating..."):
                                translated_val = translate_caption(style_val, target_lang)
                                st.markdown(f"""
                                <div class="caption-container" style="border-left-color: #3b82f6; background: rgba(59, 130, 246, 0.05);">
                                    <div class="caption-type">{target_lang} Translation</div>
                                    <div class="caption-content" style="font-style: italic;">{translated_val}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                # Copy translated button
                                st.components.v1.html(custom_copy_button(f"trans_{idx}", translated_val), height=35)
        else:
            st.info("Upload an image on the left to generate descriptions.")
        st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Batch Image Processing
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📁 Batch Upload")
    batch_files = st.file_uploader(
        "Upload multiple images to process them in batch",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key="batch_uploader"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if batch_files:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⚡ Processing Gallery")
        
        # UI controls
        col_ctrl1, col_ctrl2 = st.columns([1, 1])
        with col_ctrl1:
            batch_style = st.selectbox(
                "Export Style Variation:",
                options=["Descriptive (Default)", "Professional/SEO", "Humorous", "Creative Story", "Alt-Text (Accessibility)"],
                key="batch_style_select"
            )
        with col_ctrl2:
            include_trans = st.checkbox("Include translation in export", value=True)
            
        # Run button
        if st.button("🚀 Process All Images"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Create columns or list layout for images
            gallery_placeholder = st.container()
            
            for index, file in enumerate(batch_files):
                status_text.text(f"Processing image {index + 1} of {len(batch_files)}: {file.name}")
                
                # Load Image
                img = Image.open(file)
                
                # Generate
                base = generate_base_caption(img)
                all_styles = get_style_variations(base)
                selected_val = all_styles.get(batch_style, base)
                
                # Translate if required
                trans_val = ""
                if include_trans and target_lang != "English":
                    trans_val = translate_caption(selected_val, target_lang)
                
                # Store
                results.append({
                    "Filename": file.name,
                    "Default Caption": base,
                    "Selected Style Caption": selected_val,
                    f"Translation ({target_lang})": trans_val if trans_val else "N/A"
                })
                
                # Render in Gallery placeholder dynamically
                with gallery_placeholder:
                    col_img, col_caps = st.columns([1, 3])
                    with col_img:
                        st.image(img, use_column_width=True)
                    with col_caps:
                        st.markdown(f"#### 📄 {file.name}")
                        st.markdown(f"**Default:** {base}")
                        st.markdown(f"**Selected Style ({batch_style}):** {selected_val}")
                        if trans_val:
                            st.markdown(f"**Translation ({target_lang}):** *{trans_val}*")
                        st.markdown("<hr style='margin:10px 0; border:0; border-top:1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
                
                # Update progress
                progress_bar.progress((index + 1) / len(batch_files))
            
            status_text.success(f"Successfully processed {len(batch_files)} images!")
            
            # Create export DataFrame
            df = pd.DataFrame(results)
            
            # Export CSV button
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.markdown("### 📥 Download Results")
            st.download_button(
                label="📥 Download Captions CSV",
                data=csv_data,
                file_name="batch_captions.csv",
                mime="text/csv"
            )
            
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Upload multiple files to start batch processing.")
