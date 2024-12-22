import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_reviews_and_ratings(url):
    # PostgreSQL bağlantısı ayarları
    db_config = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432
    }

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

    def close_popup():
        """Pop-up'ı kapatma butonuna tıklar."""
        try:
            popup_close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="product-detail-app"]/div/div[2]/div/div[2]/div[2]/div/div[1]/aside/div/div/div[2]/div/div[2]/div/div/button'))
            )
            popup_close_button.click()
            print("Pop-up kapatıldı.")
        except Exception as e:
            print(f"Pop-up kapatma sırasında hata oluştu: {e}")

    try:
        # Amazon ürün sayfasına git
        driver.get(url)

        # Çerez onayını kapat
        close_cookie_consent()

        # Pop-up'ı kapat
        time.sleep(3)  # Pop-up'ın görünmesi için bekle
        close_popup()

        time.sleep(2)  # Sayfanın tam olarak yüklenmesi için bekleme

        # Ürün ismini çek
        try:
            product_name_element = driver.find_element(By.XPATH, '//h1[@class="pr-new-br" and @data-drroot="h1"]')
            product_name_parts = product_name_element.find_elements(By.TAG_NAME, 'span')
            product_name = " ".join([part.text for part in product_name_parts])
            print(f"Ürün Adı: {product_name}")
        except Exception as e:
            print(f"Ürün ismi alınamadı: {e}")
            product_name = "Bilinmiyor"

        # Yorumlar sayfasına gitmek için ilgili butona tıkla
        try:
            see_all_reviews_button = driver.find_element(By.XPATH,
                                                         '//div[contains(@class, "rvw-cnt")]/a[contains(@class, "rvw-cnt-tx")]')
            see_all_reviews_button.click()
            time.sleep(2)
            print("Yorumlar sayfasına yönlendirildi.")
        except Exception:
            print("Tüm yorumlara gitme bağlantısı bulunamadı, doğrudan yorumları toplamayı deniyoruz.")

        reviews = []
        ratings = []

        prev_length = 0  # Daha önce toplanan yorumların sayısını takip etmek için
        no_new_data_attempts = 0  # Yeni veri bulunamadığında kaç deneme yapıldığını takip etmek için

        while no_new_data_attempts < 3:  # Maksimum 3 kez yeni veri bulunamazsa durdur
            new_data_found = False  # Yeni veri bulunduğunu kontrol etmek için

            # Yorum ve yıldızları toplama döngüsü
            index = len(reviews) + 1  # Yeni başlayacağımız yorum indeksi
            while True:
                try:
                    # XPath ile yorum elemanını bulun
                    review_xpath = f'//*[@id="rating-and-review-app"]/div/div/div/div[3]/div/div/div[3]/div[2]/div[{index}]/div[2]'
                    rating_stars_xpath = f'//*[@id="rating-and-review-app"]/div/div/div/div[3]/div/div/div[3]/div[2]/div[{index}]/div[1]/div[1]/div/div'

                    review_element = driver.find_element(By.XPATH, review_xpath)
                    star_elements = driver.find_elements(By.XPATH, rating_stars_xpath)

                    # Yorumları ekle
                    reviews.append(review_element.text)

                    # Doluluk oranlarına göre yıldız sayısını hesapla
                    stars = 0
                    for star in star_elements:
                        try:
                            # Eğer dolu kısmı mevcutsa 'style' bilgisini al
                            full_star = star.find_element(By.XPATH, './div[2]')
                            style = full_star.get_attribute('style')
                            width_percentage = int(style.split("width:")[1].split("%")[0].strip())

                            if width_percentage > 50:  # %50'den büyük doluysa bir yıldız say
                                stars += 1
                        except Exception:
                            # Eğer 'div[2]' yoksa bu yıldız boş olarak değerlendirilir
                            continue

                    ratings.append(stars)

                    # Bir sonraki yoruma geçmek için indeksi artır
                    index += 1
                    new_data_found = True  # Yeni veri bulundu
                except Exception:
                    break  # Daha fazla yorum bulunamadı

            # Eğer yeni veri bulunmadıysa sayfayı kaydır
            if not new_data_found:
                current_scroll_position = driver.execute_script("return window.pageYOffset;")
                page_height = driver.execute_script("return document.body.scrollHeight;")
                next_scroll_position = current_scroll_position + (page_height * 0.35)

                driver.execute_script(f"window.scrollTo(0, {next_scroll_position});")
                time.sleep(3)  # Yeni içeriklerin yüklenmesi için bekle

                # Eğer kaydırma sonrası veri yüklenmezse deneme sayısını artır
                no_new_data_attempts += 1
            else:
                no_new_data_attempts = 0  # Yeni veri bulunduğunda sayacı sıfırla

            # Daha önceki veri uzunluğunu güncelle
            prev_length = len(reviews)

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
