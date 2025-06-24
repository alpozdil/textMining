import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# "graphics" klasörünü oluştur
if not os.path.exists("graphics"):
    os.makedirs("graphics")

# CSV dosyasını oku
df = pd.read_csv("urun_skorlari.csv")

# Ortalama skora göre sırala
df = df.sort_values(by="ortalama_skor", ascending=False)

# Grafik ayarları
plt.figure(figsize=(16, 8))  # Daha geniş alan

x = np.arange(len(df["urun_adi"]))
bar_width = 0.35

# Barlar
bars1 = plt.bar(x - bar_width/2, df["ortalama_skor"], width=bar_width, label="Ortalama Skor", color="#4A90E2")
bars2 = plt.bar(x + bar_width/2, df["hesaplanan_yildiz"], width=bar_width, label="Hesaplanan Yıldız", color="#F5A623")

# Ürün adları x ekseni
plt.xticks(x, df["urun_adi"], rotation=60, ha='right', fontsize=8)

# Etiketler ekle
for bar in bars1:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f"{yval:.2f}", ha='center', va='bottom', fontsize=7)

for bar in bars2:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f"{yval:.2f}", ha='center', va='bottom', fontsize=7)

# Eksenler ve başlık
plt.xlabel("Ürün Adı", fontsize=10)
plt.ylabel("Değer", fontsize=10)
plt.title("Ürünlere Göre Ortalama Yorum Skoru ve Hesaplanan Yıldızlar", fontsize=12)
plt.legend(fontsize=9)
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()

# Grafik kaydet
plt.savefig("graphics/urun_skor_yildiz_grafigi.png", dpi=300)
plt.show()
