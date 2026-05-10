import streamlit as st
from vector_db import VectorDatabase
from pathlib import Path
import os
import time
import torch
import re
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

# Akıllı Cevap Oluşturucu (Manuel Yükleme)
@st.cache_resource
def load_qa_model():
    # Hız ve uyumluluk için daha hafif ama keskin bir model
    model_name = "timpal0l/mdeberta-v3-base-squad2"
    try:
        with st.spinner("🤖 Akıllı analiz motoru hazırlanıyor..."):
            device = "cuda" if torch.cuda.is_available() else "cpu"
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
            model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            if device == "cuda": model = model.to("cuda")
        return tokenizer, model
    except Exception as e:
        st.error(f"Model yüklenemedi: {e}. Lütfen 'pip install tiktoken' komutunu deneyin.")
        return None, None

# Page Config
st.set_page_config(page_title="Cognitive Search Pro", page_icon="🧠", layout="wide")

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
    for word in query.split():
        if len(word) > 2:
            text = re.sub(f"({re.escape(word)})", r'<span class="highlight">\1</span>', text, flags=re.IGNORECASE)
    return text

def get_ai_answer(question, context, tokenizer, model):
    # truncation="only_second" sayesinde sorunuz korunur ve döküman metni sığdırılabildiği kadar eklenir
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = tokenizer(question, context, return_tensors="pt", truncation="only_second", max_length=512).to(device)
    
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

# Initialize Database in session state so it doesn't reload every time
if 'db' not in st.session_state:
    try:
        st.session_state.db = VectorDatabase()
        # Load index if exists
        if os.path.exists("main_index.faiss"):
            st.session_state.db.load(Path("main_index.faiss"))
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        st.stop()

# Sidebar - Data Ingestion
with st.sidebar:
    st.header("📂 Veri Yönetimi")
    uploaded_files = st.file_uploader("PDF veya Metin Dosyası Yükle", accept_multiple_files=True, type=['pdf', 'txt', 'md'])
    
    if st.button("Dökümanları İndeksle"):
        if uploaded_files:
            # Save uploaded files to a temp directory
            os.makedirs("temp_uploads", exist_ok=True)
            for uploaded_file in uploaded_files:
                with open(os.path.join("temp_uploads", uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            with st.spinner("⚡ Süper Hızlı Vektör Oluşturma Devrede..."):
                st.session_state.db.index_directory(Path("temp_uploads"), batch_size=512)
                st.session_state.db.save(Path("main_index.faiss"))
            st.success(f"{len(uploaded_files)} dosya başarıyla işlendi!")
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
            
        st.session_state.db = VectorDatabase()
        st.success("Veritabanı ve tüm önbellek tamamen temizlendi!")

    st.divider()
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
            # ID eşleşmesi varsa (Skor > 1.0), sadece o dökümanları öncelikli context yap
            exact_matches = [res.content for res in results if res.score > 1.5]
            if exact_matches:
                context = " ".join(exact_matches)
            else:
                context = " ".join([res.content for res in results[:3]])
                
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

            st.markdown(f'<div class="answer-box"><div class="ai-label">🤖 ÖZET CEVAP</div><br>{answer}</div>', unsafe_allow_html=True)
            st.subheader(f"🔍 Bilgi Kaynakları ({ (end_time-start_time)*1000:.0f}ms)")
            
            for res in results:
                display_content = highlight_text(res.content, query)
                st.markdown(f"""
                <div class="result-card">
                    <div class="pdf-title">📄 {res.metadata.get('source')}</div>
                    <div class="metadata-tag">SAYFA: {res.metadata.get('page')} • ALAKA: %{res.score*100:.0f}</div>
                    <div class="snippet">...{display_content}...</div>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Powered by FAISS, Sentence-Transformers, and Streamlit")

#to run: py -m streamlit run app.py 