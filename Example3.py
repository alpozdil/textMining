import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urlparse


def get_reviews_and_ratings(url):
    # PostgreSQL bağlantısı ayarları
    db_config = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432
    }

    # URL doğrulama
    if not (url.startswith("http://") or url.startswith("https://")):
        print("Hatalı URL girdiniz. Lütfen geçerli bir URL girin.")
        return

    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        print("Hatalı URL girdiniz. Lütfen geçerli bir URL girin.")
        return

    # Chrome seçenekleri
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Tam ekran başlatma

    # Tarayıcıyı başlat
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def close_cookie_consent():
        """Çerez onaylama butonuna tıklar."""
        try:
            consent_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
            )
            consent_button.click()
            print("Çerezler onaylandı.")
        except Exception as e:
            print(f"Çerez onayı sırasında hata oluştu: {e}")

    try:
        # Trendyol ürün sayfasına git
        driver.get(url)

        # Çerez onayını kapat
        close_cookie_consent()

        time.sleep(3)  # Sayfanın tam olarak yüklenmesi için bekleme

        # Ürün ismini çek
        try:
            product_name_element = driver.find_element(By.XPATH, '//h1[@class="pr-new-br"]')
            product_name = product_name_element.text
            print(f"Ürün Adı: {product_name}")
        except Exception as e:
            print(f"Ürün ismi alınamadı: {e}")
            product_name = "Bilinmiyor"

        # Yorumlar sayfasına gitmek için ilgili butona tıkla
        try:
            see_all_reviews_button = driver.find_element(By.XPATH,
                                                         '//div[contains(@class, "rvw-cnt")]/a[contains(@class, "rvw-cnt-tx")]')
            see_all_reviews_button.click()
            time.sleep(3)
            print("Yorumlar sayfasına yönlendirildi.")
        except Exception:
            print("Tüm yorumlara gitme bağlantısı bulunamadı, doğrudan yorumları toplamayı deniyoruz.")

        reviews = []
        ratings = []

        while True:
            try:
                # Yorumları ve yıldızları al
                review_elements = driver.find_elements(By.XPATH,
                                                        '//*[@id="rating-and-review-app"]/div/div/div/div[3]/div/div/div[3]/div[2]/div/div[2]')
                rating_elements = driver.find_elements(By.XPATH,
                                                        '//*[@id="rating-and-review-app"]/div/div/div/div[3]/div/div/div[3]/div[2]/div/div[1]/div[1]/div/div/div[2]')

                for review, rating in zip(review_elements, rating_elements):
                    reviews.append(review.text)
                    # Yıldız sayısını "width" üzerinden hesapla
                    style = rating.get_attribute("style")
                    width_percentage = int(style.split("width:")[1].split("%")[0].strip())
                    stars = width_percentage // 20  # Yıldızlar %20 oranına göre dolu
                    ratings.append(stars)

                # Sonraki sayfaya geçmek için "Sonraki" butonuna tıkla
                next_button = driver.find_element(By.XPATH, '//a[@class="next"]')
                next_button.click()
                time.sleep(3)  # Yeni sayfanın yüklenmesini bekle
            except Exception:
                print("Tüm yorumlar toplandı veya sonraki sayfa yok.")
                break

        # Veritabanına bağlan ve bilgileri kaydet
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            for i in range(len(reviews)):
                cursor.execute(
                    "INSERT INTO product_reviews (product_name, review_text, rating) VALUES (%s, %s, %s)",
                    (product_name, reviews[i], ratings[i])
                )

            conn.commit()
            print("Veriler veritabanına kaydedildi.")
        except Exception as e:
            print(f"Veritabanına kaydetme sırasında hata oluştu: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    finally:
        # İşlemler bitince tarayıcıyı kapat
        driver.quit()


if __name__ == "__main__":
    product_url = input("Lütfen Trendyol ürün linkini girin: ")
    get_reviews_and_ratings(product_url)
