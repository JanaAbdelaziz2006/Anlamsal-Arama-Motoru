import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import os
import time
import re
import base64

# Akıllı Cevap Oluşturucu (Manuel Yükleme)
@st.cache_resource
def load_qa_model():
    # Hız ve uyumluluk için daha hafif ama keskin bir model
    model_name = "timpal0l/mdeberta-v3-base-squad2"
    try:
        with st.spinner("🤖 Akıllı analiz motoru hazırlanıyor..."):
            import torch
            from transformers import AutoTokenizer, AutoModelForQuestionAnswering
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
            model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            if device == "cuda": model = model.to("cuda")
        return tokenizer, model
    except Exception as e:
        st.error(f"Model yüklenemedi: {e}. Lütfen 'pip install tiktoken' komutunu deneyin.")
        return None, None

# Global Database Instance (Shared across all users to save memory and time)
@st.cache_resource
def get_vector_db():
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
            <div style="display: flex; justify-content: center; align-items: center; height: 80vh; flex-direction: column;">
                <div style="width: 60px; height: 60px; border: 6px solid #f3f3f3; border-top: 6px solid #4285f4; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
                <h2 style="margin-top: 25px; font-family: 'Segoe UI', sans-serif; color: #4285f4; font-weight: 400;">Cognitive Search Pro Başlatılıyor</h2>
                <p style="color: #70757a; font-family: 'Segoe UI', sans-serif; font-size: 15px;">Vektör veritabanı ve AI motoru hazırlanıyor, lütfen bekleyin...</p>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            # Perform heavy initializations
            st.session_state.db = get_vector_db()
            load_qa_model() # Pre-load model to avoid wait during first search
            st.session_state.initialized = True
            time.sleep(0.5) # Smooth transition
        except Exception as e:
            st.error(f"Sistem başlatılamadı: {e}")
            st.stop()
    placeholder.empty()
# --- END PRE-LOADER ---

st.title("🧠 Cognitive Search & Knowledge Engine")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .answer-box { 
        background-color: #f0f7ff; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 8px solid #4285f4; 
        margin-bottom: 20px; 
        font-size: 18px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        color: #202124;
        line-height: 1.6;
    }
    .ai-label { 
        background-color: #4285f4; 
        color: white; 
        padding: 2px 10px; 
        border-radius: 5px; 
        font-size: 12px; 
        font-weight: bold;
        margin-bottom: 10px;
        display: inline-block;
    }
    .result-card { 
        background: white; 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 15px; 
        border: 1px solid #dfe1e5; 
        border-left: 4px solid #34a853;
    }
    .pdf-title { color: #1a0dab; font-size: 17px; font-weight: 600; }
    .metadata-tag { color: #70757a; font-size: 12px; margin-bottom: 5px; }
    .snippet { color: #3c4043; font-size: 14px; }
    .highlight { background-color: #fff9c4; font-weight: 600; padding: 0 2px; }
    </style>
    """, unsafe_allow_html=True)

def highlight_text(text, query):
    import re
    for word in query.split():
        if len(word) > 2:
            text = re.sub(f"({re.escape(word)})", r'<span class="highlight">\1</span>', text, flags=re.IGNORECASE)
    return text

def display_pdf(file_path, page_number):
    """PDF sayfasını resim olarak render eder ve st.image ile gösterir."""
    try:
        import fitz
        # PDF dosyasını aç
        doc = fitz.open(file_path)
        # Sayfa numarası metadata'da 1'den başladığı için 0-index'e çeviriyoruz
        page = doc.load_page(page_number - 1)
        # Netlik için 2x zoom ile resim oluşturuyoruz
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, caption=f"Sayfa {page_number}", use_container_width=True)
        doc.close()
    except Exception as e:
        st.error(f"Önizleme yüklenirken hata oluştu: {e}")

def get_ai_answer(question, context, tokenizer, model):
    # Sade Baseline Prompt
    full_context = "Aşağıdaki döküman içeriğine dayanarak soruyu cevapla:\n\n" + context
    
    import torch
    # truncation="only_second" sayesinde sorunuz korunur ve döküman metni sığdırılabildiği kadar eklenir
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = tokenizer(question, full_context, return_tensors="pt", truncation="only_second", max_length=512).to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    start_logits = outputs.start_logits
    end_logits = outputs.end_logits
    
    answer_start = torch.argmax(start_logits)
    answer_end = torch.argmax(end_logits) + 1
    
    answer = tokenizer.decode(inputs.input_ids[0][answer_start:answer_end], skip_special_tokens=True)
    clean_answer = answer.strip()

    # KRİTİK: Eğer cevap sadece bir sayıdan ibaretse veya sorgudaki ID ile aynıysa, 
    # model aslında soruyu cevaplamamış, sadece ID'yi bulmuş demektir.
    # Bu durumda boş dönerek 'Akıllı Yedekleme' mekanizmasını tetikliyoruz.
    if clean_answer.isdigit() or len(clean_answer) < 5:
        return ""
    
    return clean_answer

# Sidebar - Data Ingestion
with st.sidebar:
    st.header("📂 Veri Yönetimi")
    
    # 1. Mevcut Dosyaları Listele ve Yönet (Kalıcılık Bölümü)
    if os.path.exists("temp_uploads"):
        existing_files = [f for f in os.listdir("temp_uploads") if os.path.isfile(os.path.join("temp_uploads", f))]
        if existing_files:
            st.subheader("📚 Kayıtlı Dökümanlar")
            for f_name in existing_files:
                col_txt, col_btn = st.columns([0.8, 0.2])
                col_txt.caption(f"📄 {f_name}")
                if col_btn.button("❌", key=f"del_{f_name}", help="Dosyayı sil ve indeksi güncelle"):
                    os.remove(os.path.join("temp_uploads", f_name))
                    with st.spinner(f"{f_name} çıkarılıyor..."):
                        if not os.listdir("temp_uploads"):
                            # Klasör boşaldıysa her şeyi temizle
                            for f in ["main_index.faiss", "main_index.json", "documents.json"]:
                                if os.path.exists(f): os.remove(f)
                            st.cache_resource.clear()
                            st.session_state.db = get_vector_db()
                        else:
                            # Kalan dosyalarla indeksi baştan oluştur (Senkronizasyon için)
                            from vector_db import VectorDatabase
                            st.session_state.db = VectorDatabase() 
                            st.session_state.db.index_directory(Path("temp_uploads"), batch_size=512)
                            st.session_state.db.save(Path("main_index.faiss"))
                    st.rerun()
            st.divider()

    uploaded_files = st.file_uploader("PDF veya Metin Dosyası Yükle", accept_multiple_files=True, type=['pdf', 'txt', 'md'])
    
    if st.button("Dökümanları İndeksle"):
        if uploaded_files:
            # Save uploaded files to a temp directory
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
        
        # Geçici dosyaları da temizle
        if os.path.exists("temp_uploads"):
            import shutil
            shutil.rmtree("temp_uploads")
            
        st.cache_resource.clear()
        st.session_state.db = get_vector_db()
        st.success("Veritabanı ve tüm önbellek tamamen temizlendi!")

    st.divider()
    st.header("🔍 Arama Ayarları")
    sensitivity = st.slider(
        "Arama Hassasiyeti (Eşik)", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.30, 
        step=0.05,
        help="1.0: Sadece tam eşleşen kimlikleri getirir. 0.0: Her şeyi getirir."
    )
    
    col1, col2 = st.columns(2)
    col1.metric("Toplam Parça", len(st.session_state.db.documents))
    col2.metric("Hız", "O(log N)")

    st.markdown("---")
    st.header("⚙️ Teknik Mimari")
    st.caption("""
    - **Algoritma:** FAISS HNSW (Sektör Standardı)
    - **Embedding:** Sentence-Transformers
    - **Ölçekleme:** Milyon+ Doküman Kapasiteli
    - **Arama Tipi:** Cosine Similarity
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
        end_time = time.time()
        
        if not results:
            st.info("Eşleşen bir döküman bulunamadı.")
        else:
            results = [res for res in results if res.score >= sensitivity]
            context = " ".join([res.content for res in results])
                
            try:
                answer = get_ai_answer(query, context, tokenizer, model)
                
                if not answer or len(answer) < 5:
                    # Akıllı Yedekleme: Eğer AI başarısız olursa, ID'nin geçtiği yerin sonrasını ver
                    top_content = results[0].content
                    query_ids = re.findall(r'\d{9,}', query)
                    if query_ids and query_ids[0] in top_content.replace(" ", ""):
                        # Numaranın geçtiği yerden sonraki 200 karakteri al (Proje ismi oradadır)
                        start_idx = top_content.find(query_ids[0][:5]) # Kısmi arama ile bul
                        answer = top_content[start_idx:start_idx+300] + "..."
                    else:
                        sentences = re.split(r'(?<=[.!?]) +', top_content)
                        answer = " ".join(sentences[:2])
            except:
                answer = "Sonuçlar bulundu:"

            if not results:
                st.warning("Belirlenen hassasiyet seviyesinde sonuç bulunamadı. Lütfen sürgüyü sola kaydırın.")
            else:
                st.markdown(f'<div class="answer-box"><div class="ai-label">🤖 ÖZET CEVAP</div><br>{answer}</div>', unsafe_allow_html=True)
                st.subheader(f"🔍 Bilgi Kaynakları ({ (end_time-start_time)*1000:.0f}ms)")
                
                for res in results:
                    display_content = highlight_text(res.content, query)
                    # Skoru %100 ile sınırla (ID eşleşmesi 2.0 olsa bile %100 görünür)
                    display_score = min(100.0, res.score * 100)
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="pdf-title">📄 {res.metadata.get('source')}</div>
                            <div class="metadata-tag">SAYFA: {res.metadata.get('page')} • ALAKA: %{display_score:.0f}</div>
                            <div class="snippet">...{display_content}...</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # PDF Önizleme ve Dışarıda Açma İşlemleri
                        pdf_source = res.metadata.get('source')
                        pdf_path = os.path.join("temp_uploads", pdf_source)
                        
                        if os.path.exists(pdf_path):
                            with st.expander(f"👁️ Sayfa {res.metadata.get('page')} Önizle"):
                                display_pdf(pdf_path, res.metadata.get('page'))

# Footer
st.markdown("---")
st.caption("Powered by FAISS, Sentence-Transformers, and Streamlit")

#to run: py -m streamlit run app.py 
#ex: Sıralı bir dizide en hızlı arama yöntemlerinden biri hangisidir?