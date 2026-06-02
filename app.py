import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import os
import time
import re
import base64

# --- MODERN THEMES ---
THEMES = {
    "Nova": {
        'main_bg': '#f0f9ff',        # Soft sky blue
        'text_color': '#0f172a',     # Slate-900
        'box_bg': '#e0f2fe',         # Sky-100
        'box_border': '#0284c7',     # Sky-600
        'label_bg': '#0284c7',
        'card_bg': '#ffffff',
        'card_border': '#bae6fd',
        'card_left_border': '#38bdf8',
        'meta_color': '#64748b'
    },
    "Twilight": {
        'main_bg': '#fdf6f0',        # Warm creamy sunrise
        'text_color': '#2c1810',     # Warm dark espresso
        'box_bg': '#fbeee6',         # Peach-100
        'box_border': '#ca8a04',     # Terracotta
        'label_bg': '#ca8a04',
        'card_bg': '#ffffff',
        'card_border': '#fecdd3',
        'card_left_border': '#f97316',
        'meta_color': '#7c2d12'
    },
    "Midnight": {
        'main_bg': '#0b0f19',        # Deep space dark
        'text_color': '#f8fafc',     # Slate-50
        'box_bg': '#1e293b',         # Slate-800
        'box_border': '#6366f1',     # Indigo accent
        'label_bg': '#6366f1',
        'card_bg': '#111827',        # Slate-900
        'card_border': '#1f2937',
        'card_left_border': '#818cf8',
        'meta_color': '#94a3b8'
    },
    "Forest": {
        'main_bg': '#f4f6f0',        # Soft sage green
        'text_color': '#1c2d24',     # Deep pine
        'box_bg': '#e6ebe0',         # Mint-100
        'box_border': '#2d6a4f',     # Forest green
        'label_bg': '#2d6a4f',
        'card_bg': '#ffffff',
        'card_border': '#b7e4c7',
        'card_left_border': '#52b788',
        'meta_color': '#52796f'
    }
}

# Default theme state initialization
if "active_theme_name" not in st.session_state:
    st.session_state.active_theme_name = "Nova"

# Akıllı Cevap Oluşturucu (Manuel Yükleme)
@st.cache_resource
def load_qa_model():
    model_name = "savasy/bert-base-turkish-squad"
    try:
        with st.spinner("🤖 Türkçe Akıllı analiz motoru hazırlanıyor..."):
            import torch
            from transformers import AutoTokenizer, AutoModelForQuestionAnswering
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            if device == "cuda": 
                model = model.to("cuda")
        return tokenizer, model
    except Exception as e:
        st.error(f"Model yüklenemedi: {e}. Lütfen internet bağlantınızı kontrol edin.")
        return None, None

def get_db_mtime():
    """Veritabanı dosyasının son güncellenme zamanını döner."""
    return os.path.getmtime("main_index.faiss") if os.path.exists("main_index.faiss") else 0

@st.cache_resource
def get_vector_db(mtime):
    from vector_db import VectorDatabase
    db = VectorDatabase()
    if os.path.exists("main_index.faiss"):
        db.load(Path("main_index.faiss"))
    return db

# Page Config
st.set_page_config(page_title="Cognitive Search Pro", page_icon="🧠", layout="wide")

# --- PROFESSIONAL PRE-LOADER ---
if "initialized" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <div style="display: flex; justify-content: center; align-items: center; height: 70vh; flex-direction: column;">
                <div style="width: 60px; height: 60px; border: 6px solid #f3f3f3; border-top: 6px solid #4285f4; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
                <h2 style="margin-top: 25px; font-family: 'Segoe UI', sans-serif; color: #4285f4; font-weight: 400;">Cognitive Search Pro Başlatılıyor</h2>
                <p style="color: #70757a; font-family: 'Segoe UI', sans-serif; font-size: 15px;">Vektör veritabanı hazırlanıyor, lütfen bekleyin...</p>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            load_qa_model() 
            st.session_state.initialized = True
            time.sleep(0.5) 
        except Exception as e:
            st.error(f"Sistem başlatılamadı: {e}")
            st.stop()
    placeholder.empty()

st.session_state.db = get_vector_db(get_db_mtime())
# --- END PRE-LOADER ---

active_theme = THEMES[st.session_state.active_theme_name]

# --- DYNAMIC CSS INJECTION ---
# Double curly braces {{ }} prevent f-string from treating CSS selectors as Python code
st.markdown(f"""
    <style>
    .stApp {{ background-color: {active_theme['main_bg']} !important; }}
    .main {{ background-color: {active_theme['main_bg']} !important; }}
    
    /* Safely override titles and relevant structural containers without breaking pre-loaders */
    h1, h2, h3, h1 span, h2 span, h3 span {{
        color: {active_theme['text_color']} !important;
    }}
    
    /* Custom CSS to style sidebar layout columns as elegant circular picker nodes */
    div[data-testid="column"] button {{
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        min-height: 48px !important;
        padding: 0 !important;
        font-size: 20px !important;
        border: 2px solid {active_theme['card_border']} !important;
        background-color: {active_theme['card_bg']} !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08) !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    
    div[data-testid="column"] button:hover {{
        transform: scale(1.15) !important;
        border-color: {active_theme['box_border']} !important;
    }}
    
    .answer-box {{ 
        background-color: {active_theme['box_bg']}; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 8px solid {active_theme['box_border']}; 
        margin-bottom: 20px; 
        font-size: 18px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        color: {active_theme['text_color']};
        line-height: 1.6;
    }}
    .ai-label {{ 
        background-color: {active_theme['label_bg']}; 
        color: white !important; 
        padding: 2px 10px; 
        border-radius: 5px; 
        font-size: 12px; 
        font-weight: bold;
        margin-bottom: 10px;
        display: inline-block;
    }}
    .result-card {{ 
        background: {active_theme['card_bg']}; 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 15px; 
        border: 1px solid {active_theme['card_border']}; 
        border-left: 4px solid {active_theme['card_left_border']};
        color: {active_theme['text_color']};
    }}
    .pdf-title {{ color: {active_theme['box_border']} !important; font-size: 17px; font-weight: 600; }}
    .metadata-tag {{ color: {active_theme['meta_color']} !important; font-size: 12px; margin-bottom: 5px; }}
    .snippet {{ color: {active_theme['text_color']} !important; font-size: 14px; }}
    .highlight {{ background-color: #fff9c4; font-weight: 600; padding: 0 2px; color: #202124 !important; }}
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Cognitive Search & Knowledge Engine")

def highlight_text(text, query):
    for word in query.split():
        if len(word) > 2:
            text = re.sub(f"({re.escape(word)})", r'<span class="highlight">\1</span>', text, flags=re.IGNORECASE)
    return text

def display_pdf(file_path, page_number):
    try:
        import fitz
        doc = fitz.open(file_path)
        page = doc.load_page(page_number - 1)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, caption=f"Sayfa {page_number}", use_container_width=True)
        doc.close()
    except Exception as e:
        st.error(f"Önizleme yüklenirken hata oluştu: {e}")

def clean_ai_response(text):
    if not text: 
        return text
    prefixes = [r'^Kazanım\s*:', r'^Not\s*:', r'^Soru\s*:', r'^Cevap\s*:', r'^\d+\s*/\s*\d+', r'^📢', r'^⚠️', r'^Bilgi\s*:']
    for p in prefixes:
        text = re.sub(p, '', text, flags=re.IGNORECASE).strip()
    return text[:1].upper() + text[1:] if text else text 

def expand_to_sentence(answer, context):
    """Traces the extracted substring answer back to context and extracts the complete sentence."""
    if not answer or not context:
        return answer
        
    start_idx = context.lower().find(answer.lower())
    if start_idx == -1:
        return answer
        
    # Walk backward to find sentence start boundary
    sentence_start = 0
    for i in range(start_idx, -1, -1):
        if context[i] in ['.', '!', '?', '\n', '•']:
            sentence_start = i + 1
            break
            
    # Walk forward to find sentence end boundary
    sentence_end = len(context)
    for i in range(start_idx + len(answer), len(context)):
        if context[i] in ['.', '!', '?', '\n', '•']:
            sentence_end = i + 1
            break
            
    extracted_sentence = context[sentence_start:sentence_end].strip()
    # Clean leading formatting artifacts
    extracted_sentence = re.sub(r'^[-*•\s\d/]+', '', extracted_sentence)
    return extracted_sentence

def get_ai_answer(question, context, tokenizer, model, threshold=1.0): 
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = tokenizer(question, context, return_tensors="pt", truncation="only_second", max_length=512).to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    start_logits = outputs.start_logits
    end_logits = outputs.end_logits
    
    start_score = torch.max(start_logits)
    end_score = torch.max(end_logits)
    confidence = (start_score + end_score).item() 

    answer_start = torch.argmax(start_logits)
    answer_end = torch.argmax(end_logits) + 1
    
    answer = tokenizer.decode(inputs.input_ids[0][answer_start:answer_end], skip_special_tokens=True)
    clean_answer = answer.strip()

    if confidence < threshold or len(clean_answer) < 3:
        return None, 0

    if "ikili arama" in clean_answer.lower() and "binary" not in clean_answer.lower():
        clean_answer = clean_answer.replace("İkili Arama", "İkili Arama (Binary Search)").replace("ikili arama", "ikili arama (Binary Search)")
    
    return clean_answer, confidence

# Sidebar - Data Ingestion (Inside the same sidebar container block)
with st.sidebar:
    st.header("📂 Veri Yönetimi")
    
    if os.path.exists("temp_uploads"):
        existing_files = [f for f in os.listdir("temp_uploads") if os.path.isfile(os.path.join("temp_uploads", f))]
        if existing_files:
            st.subheader("📚 Kayıtlı Dökümanlar")
            for f_name in existing_files:
                col_txt, col_btn = st.columns([0.8, 0.2])
                col_txt.caption(f"📄 {f_name}")
                if col_btn.button("❌", key=f"del_{f_name}"):
                    os.remove(os.path.join("temp_uploads", f_name))
                    with st.spinner(f"{f_name} çıkarılıyor..."):
                        if not os.listdir("temp_uploads"):
                            for f in ["main_index.faiss", "main_index.json", "documents.json"]:
                                if os.path.exists(f): os.remove(f)
                            st.cache_resource.clear()
                            st.session_state.db = get_vector_db(0)
                        else:
                            from vector_db import VectorDatabase
                            st.session_state.db = VectorDatabase() 
                            st.session_state.db.index_directory(Path("temp_uploads"), batch_size=512)
                            st.session_state.db.save(Path("main_index.faiss"))
                    st.rerun()
            st.divider()

    uploaded_files = st.file_uploader("PDF veya Metin Dosyası Yükle", accept_multiple_files=True, type=['pdf', 'txt', 'md'])
    
    if st.button("Dökümanları İndeksle"):
        if uploaded_files:
            os.makedirs("temp_uploads", exist_ok=True)
            for uploaded_file in uploaded_files:
                with open(os.path.join("temp_uploads", uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            with st.spinner("⚡ Süper Hızlı Vektör Oluşturma Devrede..."):
                from vector_db import VectorDatabase
                st.session_state.db = VectorDatabase() 
                st.session_state.db.index_directory(Path("temp_uploads"), batch_size=512)
                st.session_state.db.save(Path("main_index.faiss"))
            st.success(f"{len(uploaded_files)} dosya başarıyla işlendi!")
            st.rerun()
        else:
            st.warning("Lütfen önce dosya seçin.")

    if st.button("🗑️ Veritabanını Sıfırla"):
        files_to_remove = ["main_index.faiss", "main_index.json", "documents.json"]
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)
        
        if os.path.exists("temp_uploads"):
            import shutil
            shutil.rmtree("temp_uploads")
            
        st.cache_resource.clear()
        st.session_state.db = get_vector_db(0)
        st.success("Veritabanı ve tüm önbellek tamamen temizlendi!")

    # --- INTERACTIVE CIRCLE THEME SELECTOR ---
    st.divider()
    st.header("🎨 Görünüm Teması")
    
    theme_cols = st.columns(4)
    
    with theme_cols[0]:
        # Nova: Blue circle (🔵) if active, else empty hallow circle (⚪)
        btn_label_0 = "🔵" if st.session_state.active_theme_name == "Nova" else "⚪"
        if st.button(btn_label_0, key="theme_btn_nova", help="Nova (Buz Mavisi)"):
            st.session_state.active_theme_name = "Nova"
            st.rerun()
            
    with theme_cols[1]:
        # Twilight: Orange circle (🟠) if active, else empty hallow circle (⚪)
        btn_label_1 = "🟠" if st.session_state.active_theme_name == "Twilight" else "⚪"
        if st.button(btn_label_1, key="theme_btn_twilight", help="Twilight (Sıcak Kum)"):
            st.session_state.active_theme_name = "Twilight"
            st.rerun()
            
    with theme_cols[2]:
        # Midnight: Dark circle (⚫) if active, else empty hallow circle (⚪)
        btn_label_2 = "⚫" if st.session_state.active_theme_name == "Midnight" else "⚪"
        if st.button(btn_label_2, key="theme_btn_midnight", help="Midnight (Koyu Siyah)"):
            st.session_state.active_theme_name = "Midnight"
            st.rerun()
            
    with theme_cols[3]:
        # Forest: Green circle (🟢) if active, else empty hallow circle (⚪)
        btn_label_3 = "🟢" if st.session_state.active_theme_name == "Forest" else "⚪"
        if st.button(btn_label_3, key="theme_btn_forest", help="Forest (Adaçayı)"):
            st.session_state.active_theme_name = "Forest"
            st.rerun()

    st.divider()
    st.header("🔍 Arama Ayarları")
    sensitivity = st.slider(
        "Arama Hassasiyeti (Eşik)", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.10, 
        step=0.05
    )
    
    col1, col2 = st.columns(2)
    col1.metric("Toplam Parça", len(st.session_state.db.documents))
    col2.metric("Hız", "O(log N)")

    st.markdown("---")
    st.header("⚙️ Teknik Mimari")
    st.caption("""
    - **Algoritma:** FAISS HNSW + TF-IDF Hybrid Reranker
    - **Embedding:** paraphrase-multilingual (TR optimized)
    - **QA Extraction:** savasy/bert-base-turkish-squad
    - **Arama Tipi:** Cosine Similarity + BM25 Boost
    """)

# Main Search UI
query = st.text_input("🔍 Akıllı Arama", placeholder="Örn: Binary search algoritması nedir ve karmaşıklığı ne kadardır?")
top_k = st.slider("Getirilecek sonuç sayısı", 1, 10, 3)

if query:
    tokenizer, model = load_qa_model()
    
    if tokenizer:
        start_time = time.time()
        with st.spinner("🧠 Arıyor ve analiz ediyorum..."):
            results = st.session_state.db.search(query, top_k=top_k)
            results = [res for res in results if res.score >= sensitivity]
        end_time = time.time()
        
        if not results:
            st.info("Eşleşen bir döküman bulunamadı.")
        else:
            best_answer = None
            max_confidence = -100
            target_context = None
                
            # Process extracted candidates
            for res in results:
                ans, conf = get_ai_answer(query, res.content, tokenizer, model)
                if ans and conf > max_confidence:
                    max_confidence = conf
                    best_answer = ans
                    target_context = res.content
            
            # Context-Aware Sentence Expansion
            if best_answer and target_context:
                best_answer = expand_to_sentence(best_answer, target_context)
            
            # Linguistic fallback if SQuAD output is sparse
            if not best_answer or max_confidence < 1.0 or len(best_answer) < 5:
                query_lower = query.lower()
                query_tokens = set(re.findall(r'\w+', query_lower))
                unique_ids = re.findall(r'\d{5,}', query)
                
                fallback_candidate_sentences = []
                
                for res in results:
                    sentences = re.split(r'(?<=[.!?]) +', res.content)
                    for sent in sentences:
                        sent_lower = sent.lower()
                        sentence_score = 0
                        
                        matches = sum(1 for token in query_tokens if token in sent_lower)
                        sentence_score += matches
                        
                        if unique_ids and any(uid in sent.replace(" ", "") for uid in unique_ids):
                            sentence_score += 100 
                        
                        for token in query_tokens:
                            if len(token) > 3 and sent_lower.startswith(token):
                                sentence_score += 15
                        
                        if len(sent.strip()) < 20: 
                            sentence_score -= 10
                            
                        fallback_candidate_sentences.append((sentence_score, sent.strip()))
                
                fallback_candidate_sentences.sort(key=lambda x: x[0], reverse=True)
                if fallback_candidate_sentences and fallback_candidate_sentences[0][0] > 0:
                    best_answer = fallback_candidate_sentences[0][1]
                else:
                    best_answer = results[0].content[:250] + "..."
                
            answer = clean_ai_response(best_answer)

            if not results:
                st.warning("Belirlenen hassasiyet seviyesinde sonuç bulunamadı. Lütfen sürgüyü sola kaydırın.")
            else:
                st.markdown(f'<div class="answer-box"><div class="ai-label">🤖 ÖZET CEVAP</div><br>{answer}</div>', unsafe_allow_html=True)
                st.subheader(f"🔍 Bilgi Kaynakları ({ (end_time-start_time)*1000:.0f}ms)")
                
                for res in results:
                    display_content = highlight_text(res.content, query)
                    # Limit score presentation to logical percentage
                    display_score = min(100.0, (res.score / 2.0) * 100) if res.score > 1.0 else min(100.0, res.score * 100)
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="pdf-title">📄 {res.metadata.get('source')}</div>
                            <div class="metadata-tag">SAYFA: {res.metadata.get('page')} • ALAKA: %{display_score:.0f}</div>
                            <div class="snippet">...{display_content}...</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        pdf_source = res.metadata.get('source')
                        pdf_path = os.path.join("temp_uploads", pdf_source)
                        
                        if os.path.exists(pdf_path):
                            with st.expander(f"👁️ Sayfa {res.metadata.get('page')} Önizle"):
                                display_pdf(pdf_path, res.metadata.get('page'))

# Footer
st.markdown("---")
st.caption("Powered by FAISS, Sentence-Transformers, and Streamlit")


#to run: py -m streamlit run app.py 

#ex: binary search alan karmaşıklığı nedir?
#ex: Arama algoritmalarında performans iki kritere göre değerlendirilir, nelerdir?
#ex: Bilgisiz Arama ornekleri?
#ex: 25458667405 projesi nedir?
#ex: Sıralı bir dizide en hızlı arama yöntemlerinden biri hangisidir?
#ex: DAG nedir ve hangi sistemlerde kullanılır?
#ex: Graf teorisinde bir Yol (Path) nedir?
#ex: Genişlik Öncelikli Arama (BFS) sınır veri yapısı olarak ne kullanır?
#ex: K-Means kümeleme algoritmasının temel amacı nedir?
#ex: Tekduze maliyetli arama (UCS) sınır veri yapısı olarak ne kullanır?
#ex: Derinlik Öncelikli Arama (DFS) sınır veri yapısı olarak ne kullanır?
#ex: Komşuluk Listesi bellek olarak ne kadar yer kaplar?
#ex: İkili Arama hangi paradigma ile çalışır?
IDS nedir?