from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Özel kelime listesi ve ağırlıkları
kelime_agirliklari = {
    "mükemmel": 2.0, "harika": 1.8, "kaliteli": 1.5, "güzel": 1.0, "iyi": 0.8,
    "kötü": -1.5, "berbat": -2.0, "hasarlı": -1.8, "geç": -1.2, "iade": -1.5
}

# Ürün yorumları
urun_yorumlari = [
    "Ürün mükemmel, çok kaliteli ve harika.",
    "Ürün güzel ama kargo geç geldi.",
    "Berbat bir ürün, hasarlı ve iade etmek zorunda kaldım."
]

# TF-IDF vektörleştirme: sadece belirli kelimeleri dikkate al
vectorizer = TfidfVectorizer(vocabulary=kelime_agirliklari.keys())
tfidf_matrix = vectorizer.fit_transform(urun_yorumlari)

# Kelime ağırlıklarını TF-IDF matrisine uygula
agirliklar = np.array([kelime_agirliklari[word] for word in vectorizer.get_feature_names_out()])
agirlikli_tfidf = tfidf_matrix.multiply(agirliklar)

# Sparse matrisleri dense formata dönüştür
agirlikli_tfidf_dense = agirlikli_tfidf.toarray()

# Cosine Similarity gerekliyse bu dense format kullanılabilir
print("Yoğun matris (dense format):")
print(agirlikli_tfidf_dense)

# Alternatif işlemler burada yapılabilir...
toplam_skorlar = agirlikli_tfidf_dense.sum(axis=1)

# Sonuçları göster
for idx, yorum in enumerate(urun_yorumlari):
    skor = toplam_skorlar[idx]
    print(f"Yorum: {yorum}")
    print(f"Toplam Skor: {skor:.2f}")
    if skor > 0:
        print("Değerlendirme: Olumlu")
    elif skor < 0:
        print("Değerlendirme: Olumsuz")
    else:
        print("Değerlendirme: Nötr")
    print("-" * 50)
