import psycopg2
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import string

# Türkçe stopwords listesi
turkish_stopwords = [
    'a', 'acaba', 'acep', 'adamakıllı', 'adeta', 'ait', 'altmýþ', 'altmış', 'altı', 'ama', 'amma', 'anca', 'ancak',
    'arada', 'artýk', 'aslında', 'aynen', 'ayrıca', 'az', 'açıkça', 'açıkçası', 'bana', 'bari', 'bazen', 'bazý', 'bazı',
    'başkası', 'baţka', 'belki', 'ben', 'benden', 'beni', 'benim', 'beri', 'beriki', 'beş', 'beţ', 'bilcümle', 'bile',
    'bin', 'binaen', 'binaenaleyh', 'bir', 'biraz', 'birazdan', 'birbiri', 'birden', 'birdenbire', 'biri', 'birice',
    'birileri', 'birisi', 'birkaç', 'birkaçı', 'birkez', 'birlikte', 'birçok', 'birçoğu', 'birþey', 'birþeyi', 'birşey',
    'birşeyi', 'birţey', 'bitevi', 'biteviye', 'bittabi', 'biz', 'bizatihi', 'bizce', 'bizcileyin', 'bizden', 'bize',
    'bizi', 'bizim', 'bizimki', 'bizzat', 'boşuna', 'bu', 'buna', 'bunda', 'bundan', 'bunlar', 'bunları', 'bunların',
    'bunu', 'bunun', 'buracıkta', 'burada', 'buradan', 'burası', 'böyle', 'böylece', 'böylecene', 'böylelikle',
    'böylemesine', 'böylesine', 'büsbütün', 'bütün', 'cuk', 'cümlesi', 'da', 'daha', 'dahi', 'dahil', 'dahilen', 'daima',
    'dair', 'dayanarak', 'de', 'defa', 'dek', 'demin', 'demincek', 'deminden', 'denli', 'derakap', 'derhal', 'derken',
    'deđil', 'değil', 'değin', 'diye', 'diđer', 'diğer', 'diğeri', 'doksan', 'dokuz', 'dolayı', 'dolayısıyla', 'doğru',
    'dört', 'edecek', 'eden', 'ederek', 'edilecek', 'ediliyor', 'edilmesi', 'ediyor', 'elbet', 'elbette', 'elli', 'emme',
    'en', 'enikonu', 'epey', 'epeyce', 'epeyi', 'esasen', 'esnasında', 'etmesi', 'etraflı', 'etraflıca', 'etti',
    'ettiği', 'ettiğini', 'evleviyetle', 'evvel', 'evvela', 'evvelce', 'evvelden', 'evvelemirde', 'evveli', 'eđer',
    'eğer', 'fakat', 'filanca', 'gah', 'gayet', 'gayetle', 'gayri', 'gayrı', 'gelgelelim', 'gene', 'gerek', 'gerçi',
    'geçende', 'geçenlerde', 'gibi', 'gibilerden', 'gibisinden', 'gine', 'göre', 'gırla', 'hakeza', 'halbuki', 'halen',
    'halihazırda', 'haliyle', 'handiyse', 'hangi', 'hangisi', 'hani', 'hariç', 'hasebiyle', 'hasılı', 'hatta', 'hele',
    'hem', 'henüz', 'hep', 'hepsi', 'her', 'herhangi', 'herkes', 'herkesin', 'hiç', 'hiçbir', 'hiçbiri', 'hoş',
    'hulasaten', 'iken', 'iki', 'ila', 'ile', 'ilen', 'ilgili', 'ilk', 'illa', 'illaki', 'imdi', 'indinde', 'inen',
    'insermi', 'ise', 'ister', 'itibaren', 'itibariyle', 'itibarıyla', 'iyi', 'iyice', 'iyicene', 'için', 'iş', 'işte',
    'iţte', 'kadar', 'kaffesi', 'kah', 'kala', 'kanýmca', 'karşın', 'katrilyon', 'kaynak', 'kaçı', 'kelli', 'kendi',
    'kendilerine', 'kendini', 'kendisi', 'kendisine', 'kendisini', 'kere', 'kez', 'keza', 'kezalik', 'keşke', 'keţke',
    'ki', 'kim', 'kimden', 'kime', 'kimi', 'kimisi', 'kimse', 'kimsecik', 'kimsecikler', 'külliyen', 'kýrk', 'kýsaca',
    'kırk', 'kısaca', 'lakin', 'leh', 'lütfen', 'maada', 'madem', 'mademki', 'mamafih', 'mebni', 'međer', 'meğer',
    'meğerki', 'meğerse', 'milyar', 'milyon', 'mu', 'mü', 'mý', 'mı', 'nasýl', 'nasıl', 'nasılsa', 'nazaran', 'naşi',
    'ne', 'neden', 'nedeniyle', 'nedenle', 'nedense', 'nerde', 'nerden', 'nerdeyse', 'nere', 'nerede', 'nereden',
    'neredeyse', 'neresi', 'nereye', 'netekim', 'neye', 'neyi', 'neyse', 'nice', 'nihayet', 'nihayetinde', 'nitekim',
    'niye', 'niçin', 'o', 'olan', 'olarak', 'oldu', 'olduklarını', 'oldukça', 'olduğu', 'olduğunu', 'olmadı',
    'olmadığı', 'olmak', 'olması', 'olmayan', 'olmaz', 'olsa', 'olsun', 'olup', 'olur', 'olursa', 'oluyor', 'on',
    'ona', 'onca', 'onculayın', 'onda', 'ondan', 'onlar', 'onlardan', 'onlari', 'onlarýn', 'onları', 'onların', 'onu',
    'onun', 'oracık', 'oracıkta', 'orada', 'oradan', 'oranca', 'oranla', 'oraya', 'otuz', 'oysa', 'oysaki', 'pek',
    'pekala', 'peki', 'pekçe', 'peyderpey', 'rağmen', 'sadece', 'sahi', 'sahiden', 'sana', 'sanki', 'sekiz', 'seksen',
    'sen', 'senden', 'seni', 'senin', 'siz', 'sizden', 'sizi', 'sizin', 'sonra', 'sonradan', 'sonraları', 'sonunda',
    'tabii', 'tam', 'tamam', 'tamamen', 'tamamıyla', 'tarafından', 'tek', 'trilyon', 'tüm', 'var', 'vardı', 'vasıtasıyla',
    've', 'velev', 'velhasıl', 'velhasılıkelam', 'veya', 'veyahut', 'ya', 'yahut', 'yakinen', 'yakında', 'yakından',
    'yakınlarda', 'yalnız', 'yalnızca', 'yani', 'yapacak', 'yapmak', 'yaptı', 'yaptıkları', 'yaptığı', 'yaptığını',
    'yapılan', 'yapılması', 'yapıyor', 'yedi', 'yeniden', 'yenilerde', 'yerine', 'yetmiþ', 'yetmiş', 'yetmiţ', 'yine',
    'yirmi', 'yok', 'yoksa', 'yoluyla', 'yüz', 'yüzünden', 'zarfında', 'zaten', 'zati', 'zira', 'çabuk', 'çabukça',
    'çeşitli', 'çok', 'çokları', 'çoklarınca', 'çokluk', 'çoklukla', 'çokça', 'çoğu', 'çoğun', 'çoğunca', 'çoğunlukla',
    'çünkü', 'öbür', 'öbürkü', 'öbürü', 'önce', 'önceden', 'önceleri', 'öncelikle', 'öteki', 'ötekisi', 'öyle', 'öylece',
    'öylelikle', 'öylemesine', 'öz', 'üzere', 'üç', 'þey', 'þeyden', 'þeyi', 'þeyler', 'þu', 'þuna', 'þunda', 'þundan',
    'þunu', 'şayet', 'şey', 'şeyden', 'şeyi', 'şeyler', 'şu', 'şuna', 'şuncacık', 'şunda', 'şundan', 'şunlar', 'şunları',
    'şunu', 'şunun', 'şura', 'şuracık', 'şuracıkta', 'şurası', 'şöyle', 'ţayet', 'ţimdi', 'ţu', 'ţöyle'
    ]


# PostgreSQL bağlantısı ayarları
db_config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': 5432
}


def fetch_reviews_with_ids():
    """Veritabanından id ve yorumları çeker."""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, review_text FROM product_reviews")
        reviews = cursor.fetchall()
        # reviews, [(id1, yorum1), (id2, yorum2), ...] şeklinde olur
        return reviews
    except Exception as e:
        print(f"Veritabanından veriler alınırken hata oluştu: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()


def preprocess_text(text):
    """Metni temizler ve word cloud için hazırlar."""
    # Küçük harfe çevir
    text = text.lower()

    # Noktalama işaretlerini kaldır
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Tokenize et ve stopwords'leri çıkar
    tokens = text.split()
    tokens = [word for word in tokens if word not in turkish_stopwords]

    # Temizlenmiş metni tekrar birleştir
    cleaned_text = " ".join(tokens)
    return cleaned_text


def create_wordcloud(text, id, output_dir="wordclouds"):
    """Word Cloud oluşturur ve kaydeder."""
    # WordCloud oluşturma
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=turkish_stopwords,
        max_words=200,
        collocations=False
    ).generate(text)

    # Klasör oluştur (eğer yoksa)
    os.makedirs(output_dir, exist_ok=True)

    # Görseli kaydet
    output_path = os.path.join(output_dir, f"wordcloud_{id}.png")
    wordcloud.to_file(output_path)
    print(f"Word Cloud kaydedildi: {output_path}")

    # İsterseniz görselleştirme yapabilirsiniz
    # plt.figure(figsize=(15, 7.5))
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis('off')
    # plt.show()


if __name__ == "__main__":
    # Veritabanından id ve yorumları çek
    reviews_with_ids = fetch_reviews_with_ids()

    if not reviews_with_ids:
        print("Veritabanından yorum alınamadı veya yorum yok.")
    else:
        for id, review_text in reviews_with_ids:
            # Yorumları temizle
            cleaned_text = preprocess_text(review_text)

            # Word Cloud oluştur ve kaydet
            create_wordcloud(cleaned_text, id)
