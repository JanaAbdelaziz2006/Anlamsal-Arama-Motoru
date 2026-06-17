Projenin sunumu (Presentation):
[updated sunum.pptx](https://github.com/user-attachments/files/29057918/updated.sunum.pptx)

Projenin interface:
<img width="1920" height="850" alt="image" src="https://github.com/user-attachments/assets/e2204424-7551-442c-b7b4-3b3b05c1a0cb" />
<img width="1920" height="850" alt="image" src="https://github.com/user-attachments/assets/69544068-d649-41c1-8cb7-bd3ad975c9f0" />
<img width="1920" height="843" alt="image" src="https://github.com/user-attachments/assets/ab8bd321-bdd8-4ed3-933b-81639c04b2c0" />
<img width="1919" height="831" alt="image" src="https://github.com/user-attachments/assets/de67ba94-e961-4dfc-a9d9-063672db2941" />
<img width="1919" height="840" alt="image" src="https://github.com/user-attachments/assets/890de8ef-9f57-4fa8-95f9-57fccb5d4fcd" />
<img width="1920" height="842" alt="image" src="https://github.com/user-attachments/assets/e30429fd-f275-474a-8e75-6770d9523942" />





# Professional Vector Database (VectorDB) System

Profesyonel, nesne yönelimli (OOP) ve yüksek performanslı bir Vektör Veritabanı sistemi.

## 🎯 Özellikler

### 1. **Embedding (Vektör Oluşturma)**
- ✅ `sentence-transformers` (paraphrase-multilingual-MiniLM-L12-v2) kullanımı
- ✅ Toplu embedding işlemleri (batch processing)
- ✅ Optimal boyut: 384-dimansiyonal vektörler
- ✅ Hata yönetimi ve loglama

### 2. **Indexing (Dizin Oluşturma)**
- ✅ FAISS IndexHNSWFlat algoritması
- ✅ Milyonlarca doküman için optimize edilmiş
- ✅ Hızlı arama: O(log n) kompleksitesi
- ✅ Disk'e kaydetme ve yükleme desteği

### 3. **Veri Yönetimi (Data Management)**
- ✅ Generator-based veri yükleme (hafıza tasarrufu)
- ✅ JSONL dosya formatı desteği
- ✅ Disk'ten akış bazlı okuma
- ✅ Milyonlarca satırda RAM patlaması olmaz

### 4. **Arama (Search)**
- ✅ Kosinüs benzerliği (Cosine Similarity) temelli
- ✅ Anlamsal arama (Semantic Search)
- ✅ Benzerlik puanları (0-1 aralığında)
- ✅ Configurable top-k sonuçlar

### 5. **Hata Yönetimi (Error Handling)**
- ✅ Özel hata sınıfları (Custom Exceptions)
- ✅ Kapsamlı logging sistemi
- ✅ Dosya ve konsol çıktısı
- ✅ Detaylı error mesajları

### 6. **Temiz Kod (Clean Code)**
- ✅ OOP mimarisi (Object-Oriented Programming)
- ✅ Modüler yapı (Modular Design)
- ✅ Type hints (Python type annotations)
- ✅ Açıklayıcı docstrings
- ✅ SOLID prensipleri

---

## 📦 Kurulum

### Gereksinimler
- Python 3.8+
- pip (Python package manager)

### Adım 1: Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

**Kurulum süresi:** ~5-10 dakika (modelleri indirme nedeniyle)

### Gerekli Paketler

```
sentence-transformers==3.0.1
faiss-cpu==1.7.4
numpy==1.24.3
```

---

## 🚀 Hızlı Başlangıç

### Basit Örnek

```python
from vector_db import VectorDatabase
from pathlib import Path

# 1. Veritabanını Oluştur
db = VectorDatabase()

# 2. Dokümanları İndeksle
db.index_documents(Path("data.jsonl"), batch_size=32)

# 3. Arama Yap
results = db.search("machine learning", top_k=10)

# 4. Sonuçları Görüntüle
for result in results:
    print(f"ID: {result.document_id}")
    print(f"Benzerlik: {result.score:.4f}")
    print(f"İçerik: {result.content}")
    print()

# 5. Veritabanını Kaydet
db.save(Path("vector_db_index.faiss"))
```

---

## 📝 Veri Format (JSONL)

Veri dosyası JSONL formatında olmalıdır (her satır bir JSON):

```jsonl
{"id": "doc_000001", "content": "Bu bir test dokümandır", "metadata": {"source": "test"}}
{"id": "doc_000002", "content": "Machine learning çok güçlüdür", "metadata": {"source": "test"}}
{"id": "doc_000003", "content": "Python programlama dili popülerdir", "metadata": {"source": "test"}}
```
## 📝 Veri Format (pdf,txt)

Kullanıcı herhangi bir dosya pdf-txt yükleyebilir ve 100000 tane dosya koysa da fark etmez


### Gerekli Alanlar
- `id`: Unique document identifier (string)
- `content`: Dokuman metin içeriği (string)
- `metadata` (opsiyonel): İlave bilgiler (dict)

---

## 🏗️ Sistem Mimarisi

```
VectorDatabase (Ana Sınıf)
│
├── EmbeddingManager (Embedding Yönetimi)
│   ├── Model Loading (Transformers)
│   ├── Single Embedding (Tek Metin)
│   └── Batch Embedding (Toplu)
│
├── FAISSIndexManager (Dizin Yönetimi)
│   ├── HNSW Index Creation
│   ├── Add Embeddings
│   ├── Search
│   ├── Save/Load
│   └── Document Mapping
│
└── DataLoader (Veri Yükleme)
    ├── Generator-based Loading
    ├── JSONL Parsing
    └── Validation
```

---

## 📚 Ana Sınıflar ve Fonksiyonlar

### VectorDatabase

```python
class VectorDatabase:
    def __init__(self, embedding_model: str = "multilingual-MiniLM-L12-v2")
    def index_documents(self, data_file: Path, batch_size: int = 32)
    def search(self, query: str, top_k: int = 10) -> List[SearchResult]
    def save(self, index_path: Path)
    def load(self, index_path: Path)
```

### EmbeddingManager

```python
class EmbeddingManager:
    def __init__(self, model_name: str = "multilingual-MiniLM-L12-v2")
    def embed(self, text: str) -> np.ndarray
    def embed_batch(self, texts: List[str]) -> np.ndarray
```

### FAISSIndexManager

```python
class FAISSIndexManager:
    def __init__(self, embedding_dim: int, max_connections: int = 32)
    def add_embeddings(self, embeddings: np.ndarray, doc_ids: List[str])
    def search(self, query_embedding: np.ndarray, k: int = 10)
    def save_index(self, filepath: Path)
    def load_index(self, filepath: Path)
```

### DataLoader

```python
class DataLoader:
    def __init__(self, data_file: Path)
    def load_documents(self, max_documents: Optional[int] = None) -> Generator[Document]
```

---

## 🧪 Demolar Çalıştırma

Kapsamlı demolar çalıştırmak için:

```bash
python demo.py
```

### Dahil Edilen Demolar

1. **Basic Indexing and Search** - Basit indexing ve arama
2. **Persistent Storage** - Veritabanını disk'e kaydetme/yükleme
3. **Error Handling** - Hata yönetimi örnekleri
4. **Batch Operations** - Toplu işlemler
5. **Similarity Scores** - Benzerlik puanları analizi

---

## 🔍 Arama Örnekleri

### Örnek 1: Temel Arama

```python
results = db.search("artificial intelligence", top_k=5)
for result in results:
    print(f"{result.score:.4f} - {result.content}")
```

### Örnek 2: Anlamsal Arama

```python
# "deep learning" sorgusuna benzer anlamı olan dokümanları bul
results = db.search("neural networks learning", top_k=10)
```

### Örnek 3: Büyük Veri

```python
# 1 milyon dokümanı index'le
db.index_documents("large_dataset.jsonl", batch_size=64, max_documents=1_000_000)

# Hızlı arama
results = db.search("your query", top_k=20)
```

---

## 📊 Performans Özellikleri

### Embedding Boyutu
- Model: multilingual-MiniLM-L12-v2
- Boyut: 384 dimensyon
- Hız: ~1000 saniye/dokuman (GPU'da daha hızlı)

### İndeksleme Hızı
- HNSW: Linear time O(n log n)
- Memory: ~200 KB/dokuman (float32 + overhead)

### Arama Hızı
- HNSW Search: O(log n) averages
- 1 Milyon dokuman: ~50-100ms

### Bellek Kullanımı
- Generator-based loading: Sabit bellek
- Batch processing: batch_size * 384 * 4 bytes

---

## 🛠️ İleri Kullanım

### 1. Özel Model Kullanımı

```python
# Farklı embedding modeli kullan
db = VectorDatabase(embedding_model="all-mpnet-base-v2")
```

### 2. Batch Size Ayarlama

```python
# Daha hızlı ancak daha çok bellek kullan
db.index_documents("data.jsonl", batch_size=64)

# Daha yavaş ancak daha az bellek kullan
db.index_documents("data.jsonl", batch_size=8)
```

### 3. En Fazla Doküman Sınırı

```python
# Yalnızca ilk 10,000 dokümanı indexle
db.index_documents("large_data.jsonl", max_documents=10_000)
```

### 4. Loglama Kontrol

```python
import logging
logging.getLogger("VectorDB").setLevel(logging.DEBUG)  # Debug mod
```

---

## ⚠️ Hata Yönetimi

### Özel Hata Sınıfları

```python
from vector_db import (
    VectorDBException,
    EmbeddingException,
    IndexingException,
    SearchException,
    DataLoadingException
)

try:
    db.search(query)
except SearchException as e:
    print(f"Arama hatası: {e}")
except VectorDBException as e:
    print(f"Genel VectorDB hatası: {e}")
```

---

## 📋 Dosya Yapısı

```
project.py/
├── vector_db.py          # Ana VectorDB sistemi
├── demo.py               # Kapsamlı demolar
├── requirements.txt      # Python bağımlılıkları
├── README.md             # Bu dosya
└── start.py              # Ana başlangıç dosyası
```

---

## 🔐 Güvenlik Notları

1. **Veri Doğrulama**: Tüm girdiler doğrulanır
2. **Exception Handling**: Kapsamlı hata yönetimi
3. **Loglama**: Tüm işlemler loglanır (debug için)
4. **Type Hints**: Tür güvenliği

---

## 📈 İyileştirme Önerileri

Gelecekteki geliştirmeler:

- [ ] GPU/CUDA desteği (faiss-gpu)
- [ ] Distributed indexing (parallelization)
- [ ] Query caching mechanism
- [ ] Index compression
- [ ] Real-time updates
- [ ] Multi-modal embeddings
- [ ] Clustering functionality
- [ ] Visualization tools

---

## 🤝 Katkıda Bulunma

Buglar, öneriler ve iyileştirmeler için:

1. İssue açın
2. Pull request gönderin
3. Feedback sağlayın

---

## 📞 Destek

Sorunlar ve sorular için:

- Log dosyasını kontrol edin: `vector_db.log`
- Error message'ını okuyun (açıklayıcı olacak şekilde tasarlanmıştır)
- Demolar çalıştırarak sistemin düzgün çalıştığını doğrulayın

---

## 📄 Lisans

MIT License - Açık kaynak ve ticari kullanım için ücretsiz

---

## 📖 Kaynaklar

- [Sentence Transformers](https://www.sbert.net/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [NumPy Docs](https://numpy.org/doc/)
- [Vector Databases](https://en.wikipedia.org/wiki/Vector_database)

---

**Son Güncelleme:** Haziran 2026

**Durum:** ✅ Production Ready
