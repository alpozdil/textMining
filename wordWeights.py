import psycopg2
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import string
import re
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
    'çeşitli', 'çok', 'çokları', 'çoklarınca', 'çokluk', 'çoklukla', 'çokça', 'çünkü', 'öbür', 'öbürkü', 'önce', 'önceden',
    'önceleri', 'öncelikle', 'öteki', 'öyle', 'öylece', 'öylelikle', 'öylemesine', 'öylesine', 'üzere', 'üstelik', 'üç',
    'þayet', 'þey', 'şayet', 'şey', 'şeyden', 'şeye', 'şeyi', 'şeyler', 'şöyle', 'şu', 'şuna', 'şuncacık', 'şunda',
    'şundan', 'şunlar', 'şunları', 'şunların', 'şunu', 'şunun', 'şura', 'şuracık', 'şuracıkta', 'şurası', 'şöyle'
]

# PostgreSQL bağlantısı
try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    print("Bağlantı başarılı!")
except Exception as e:
    print(f"Bağlantı hatası: {e}")
    exit()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, review_text FROM product_reviews")  # Tablo adını ve sütunları kontrol et
    rows = cursor.fetchall()

    # WordCloud klasörünü oluştur
    os.makedirs("WordClouds", exist_ok=True)

    yorumlar_dict = {}
    for product_name, yorum in rows:
        # Geçersiz karakterleri temizle
        valid_product_name = re.sub(r'[<>:"/\\|?*]', '_', product_name.strip().replace(" ", "_"))
        if valid_product_name not in yorumlar_dict:
            yorumlar_dict[valid_product_name] = []
        yorumlar_dict[valid_product_name].append(yorum)

    for product_name, yorum_listesi in yorumlar_dict.items():
        birlesik_yorumlar = " ".join(yorum_listesi).lower().translate(str.maketrans('', '', string.punctuation))
        kelimeler = [kelime for kelime in birlesik_yorumlar.split() if kelime not in turkish_stopwords]

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            contour_width=2,  # Kenarlık kalınlığı
            contour_color="red"  # Kenarlık rengi
        ).generate(" ".join(kelimeler))

        # WordCloud kaydet
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        file_path = f"WordClouds/{product_name}.png"
        plt.savefig(file_path)
        plt.close()
        print(f"{file_path} kaydedildi.")

        # Kelime ağırlıklarını konsolda yazdır
        print(f"\n'{product_name}' için kelime ağırlıkları:")
        kelime_agirliklari = wordcloud.words_  # Kelime ve ağırlık sözlüğü
        for kelime, agirlik in kelime_agirliklari.items():
            print(f"{kelime}: {agirlik}")

except Exception as e:
    print(f"İşlem hatası: {e}")
finally:
    cursor.close()
    conn.close()
    print("Bağlantı kapatıldı.")
