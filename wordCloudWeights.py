import psycopg2
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import string
import re

# Türkçe stopwords listesi
turkish_stopwords = ['a', 'acaba', 'acep', 'adamakıllı', 'adeta', 'ait', 'altmýþ', 'altmış', 'altı', 'ama', 'amma', 'anca', 'ancak',
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
    'şundan', 'şunlar', 'şunları', 'şunların', 'şunu', 'şunun', 'şura', 'şuracık', 'şuracıkta', 'şurası', 'şöyle']

# Kelime ağırlıkları (senin tanımladığın şekilde)
kelime_agirliklari = {
    "mükemmel": 2.0, "harika": 1.8, "kaliteli": 1.5, "güzel": 1.0, "iyi": 0.8,
    "kusursuz": 2.0, "olumlu": 1.7, "memnun": 1.5, "keyifli": 1.4, "uygun": 1.2,
    "faydalı": 1.6, "beğendim": 1.5, "hızlı": 1.4, "şık": 1.3, "müthiş": 1.9,
    "özenli": 1.6, "rahat": 1.4, "başarılı": 1.8, "düzgün": 1.2, "dostane": 1.3,
    "etkileyici": 1.9, "iyi iş": 1.7, "mükemmel hizmet": 2.0, "uyumlu": 1.2,
    "dayanıklı": 1.5, "mutlu": 1.8, "kalite": 1.6, "kolay": 1.2, "konforlu": 1.4,
    "zarif": 1.5, "kibar": 1.3, "teşekkür ederim": 1.6, "tatlı": 1.4,
    "çok teşekkürler": 1.7, "bayıldım": 1.9, "tavsiye ederim": 1.8,
    "kullanışlı": 1.6, "şık duruyor": 1.5, "zarif duruyor": 1.5,
    "beğendi": 1.4, "ürün güzel": 1.6, "harika güzeldi": 1.8,
    "hızlı sağlam": 1.7, "güzel alın": 1.5, "naif": 1.3, "sorunsuz": 1.4,
    "almıştım beğendi": 1.4, "severek kullanıyorum": 1.6, "aldım uygun": 1.3,
    "beğendik": 1.4, "mükemmel sevdim": 2.0, "duruyor": 1.0,
    "elime ulaştı": 1.4, "fiyat performans": 1.6, "alabilirsiniz": 1.5,
    "özenli göründüğü": 1.6, "geldi rahat": 1.4, "duruşu tatlı": 1.5,
    "aynısı beğendi": 1.5, "ideal": 1.3, "begendim": 1.4,
    "kendime alacağım": 1.6, "severek kullanıyor": 1.7, "alın aldırın": 1.5,
    "ulaştı elime": 1.4, "hızlı ulaştı": 1.5, "kargo hızlıydı": 1.5,
    "aldım beğenildi": 1.6, "özenle parça": 1.5, "güzell": 1.4,
    "severek çalışıyor": 1.5, "bayıldımmm": 2.0, "inanılmaz": 1.9,
    "tavsiye ediyorum": 1.9, "ulaştı öneririm": 1.6, "narin": 1.5,
    "iyiydi": 1.4, "kalitesi": 1.6, "beyendim": 1.4,
    "bayıldımmmm": 2.0, "memnun kaldım": 1.7, "almanızı tavsiye": 1.9,
    "hızlı teslimat": 1.6, "hoşuma gitti": 1.5, "hizli": 1.4, "bayıldımm": 2.0,

    # Negatif kelimeler
    "kötü": -1.5, "berbat": -2.0, "hasarlı": -1.8, "geç": -1.2, "iade": -1.5,
    "bozuk": -1.7, "dikkatsiz": -1.4, "uygunsuz": -1.6, "kırık": -1.8, "problemli": -1.5,
    "yanlış": -1.3, "eksik": -1.7, "yavaş": -1.4, "kalitesiz": -1.8, "hayal kırıklığı": -2.0,
    "korkunç": -2.0, "fiyasko": -2.0, "sinir bozucu": -1.8, "beğenmedim": -1.5, "rahatsız": -1.4,
    "yetersiz": -1.6, "gereksiz": -1.3, "saygısız": -1.9, "memnuniyetsiz": -1.8, "kaba": -1.5,
    "rezalet": -2.0, "pişmanlık": -1.7, "kaos": -1.9, "uygunsuzluk": -1.5, "zorlayıcı": -1.2,
    "güvensiz": -1.8, "hüsran": -1.9, "yıkık": -1.7, "çirkin": -1.6, "kullanışsız": -1.8
}

# Yeni yıldız hesaplama (yorum sayısını dikkate alan)
def hesapla_yildiz(toplam_skor, yorum_sayisi):
    if yorum_sayisi == 0:
        return 0.0
    ortalama_skor = toplam_skor / yorum_sayisi
    normalize_edilmis = max(min((ortalama_skor + 1.5) / 3.0 * 5.0, 5.0), 0.5)
    return round(normalize_edilmis, 1)

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
    cursor.execute("SELECT product_name, review_text FROM product_reviews")
    rows = cursor.fetchall()

    os.makedirs("WordClouds", exist_ok=True)

    yorumlar_dict = {}
    for product_name, yorum in rows:
        valid_product_name = re.sub(r'[<>:"/\\|?*]', '_', product_name.strip().replace(" ", "_"))
        if valid_product_name not in yorumlar_dict:
            yorumlar_dict[valid_product_name] = []
        yorumlar_dict[valid_product_name].append(yorum)

    for product_name, yorum_listesi in yorumlar_dict.items():
        birlesik_yorumlar = " ".join(yorum_listesi).lower().translate(str.maketrans('', '', string.punctuation))
        kelimeler = [kelime for kelime in birlesik_yorumlar.split() if kelime not in turkish_stopwords]

        toplam_skor = sum(kelime_agirliklari.get(k, 0) for k in kelimeler)
        yorum_sayisi = len(yorum_listesi)
        yildiz = hesapla_yildiz(toplam_skor, yorum_sayisi)

        # WordCloud oluştur
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            contour_width=2,
            contour_color="red"
        ).generate(" ".join(kelimeler))

        # Kaydet
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"{product_name} - {yildiz} ⭐", fontsize=16)
        path = f"WordClouds/{product_name}.png"
        plt.savefig(path)
        plt.close()
        print(f"{path} kaydedildi.")

        # Konsola yaz
        print(f"\n'{product_name}' için:")
        print(f"- Yorum Sayısı: {yorum_sayisi}")
        print(f"- Toplam Skor: {toplam_skor:.2f}")
        print(f"- Ortalama Skor: {toplam_skor / yorum_sayisi:.2f}" if yorum_sayisi > 0 else "- Ortalama Skor: 0")
        print(f"- Hesaplanan Yıldız: {yildiz}")

except Exception as e:
    print(f"İşlem hatası: {e}")
finally:
    cursor.close()
    conn.close()
    print("Bağlantı kapatıldı.")