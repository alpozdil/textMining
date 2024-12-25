import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def search_and_click_on_products(search_term):

    # PostgreSQL bağlantısı ayarları
    global cursor, cursor
    db_config = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432
    }

    # Chrome seçenekleri
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Tarayıcıyı tam ekran başlat

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
        # Trendyol ana sayfasına git
        driver.get("https://www.trendyol.com")

        # Çerez onayını kapat
        close_cookie_consent()

        # Arama çubuğunu bul ve arama terimini yaz
        try:
            search_bar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="sfx-discovery-search-suggestions"]/div/div/input'))
            )
            search_bar.send_keys(search_term)  # Arama terimini yaz
            search_bar.send_keys(Keys.ENTER)  # Enter tuşuna basarak arama yap
            print(f"{search_term} için arama yapıldı.")
            time.sleep(3)  # Arama sonuçlarının yüklenmesi için bekle
        except Exception as e:
            print(f"Arama çubuğu bulunamadı veya işlem başarısız oldu: {e}")

        # Sayfadaki ürün başlıklarını bul ve tıkla
        try:
            product_titles = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'h3.prdct-desc-cntnr-ttl-w'))
            )
            print(f"{len(product_titles)} adet ürün bulundu. Ürünlere tıklanıyor...")

            # Her bir ürün başlığı için döngü
            for index, title in enumerate(product_titles[:2]):  # İlk 2 ürüne tıklayalım
                try:

                    # Ürünün bağlantısını almak için üst etikete erişiyoruz
                    product_element = title.find_element(By.XPATH, "./ancestor::a")  # Bağlantı elemanını bul
                    product_url = product_element.get_attribute("href")  # URL'yi al

                    # Yeni bir sekme aç ve URL'yi orada işleme al
                    driver.execute_script("window.open(arguments[0]);", product_url)

                    # Yeni sekmeye geç
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(3)  # Ürün sayfasının yüklenmesini bekle

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
                                EC.element_to_be_clickable((By.XPATH,
                                                            '//*[@id="product-detail-app"]/div/div[2]/div/div[2]/div[2]/div/div[1]/aside/div/div/div[2]/div/div[2]/div/div/button'))
                            )
                            popup_close_button.click()
                            print("Pop-up kapatıldı.")
                        except Exception as e:
                            print(f"Pop-up kapatma sırasında hata oluştu: {e}")

                    try:

                        # Pop-up'ı kapat
                        time.sleep(2)  # Pop-up'ın görünmesi için bekle
                        if index == 0:
                            close_popup()

                        time.sleep(2)  # Sayfanın tam olarak yüklenmesi için bekleme

                        # Ürün ismini çek
                        try:
                            product_name_element = driver.find_element(By.XPATH,
                                                                       '//h1[@class="pr-new-br" and @data-drroot="h1"]')
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
                                next_scroll_position = current_scroll_position + (page_height * 0.27)

                                driver.execute_script(f"window.scrollTo(0, {next_scroll_position});")
                                time.sleep(2)  # Yeni içeriklerin yüklenmesi için bekle

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


                     driver.close()

                    # Ana sekmeye geri dön
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    print(f"{index + 1}. ürüne tıklanırken hata oluştu: {e}")

        except Exception as e:
            print(f"Ürün başlıkları bulunamadı: {e}")

    finally:
        # Tarayıcıyı kapat
        time.sleep(3)
        driver.quit()


if __name__ == "__main__":
    # Kullanıcıdan arama terimini al
    search_term = input("Aramak istediğiniz kelimeyi girin: ")
    search_and_click_on_products(search_term)
