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


def close_cookie_consent(driver):
    try:
        consent_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
        )
        consent_button.click()
        print("Çerezler onaylandı.")
    except Exception as e:
        print(f"Çerez onayı sırasında hata oluştu: {e}")


def close_initial_popup(driver):
    try:
        popup_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="envoy"]/div/div[1]/div[2]/div/div[3]/div/div/button'))
        )
        popup_button.click()
        print("İlk ürün pop-up'ı kapatıldı.")
    except Exception as e:
        print(f"İlk ürün pop-up'ı kapatılamadı (muhtemelen görünmedi): {e}")


def scroll_until_element_found(driver, by, value, max_scrolls=15, scroll_pause=1.5):
    for i in range(max_scrolls):
        try:
            element = driver.find_element(by, value)
            print(f"{i + 1}. kaydırmada buton bulundu.")
            return element
        except:
            driver.execute_script("window.scrollBy(0, window.innerHeight * 0.1);")
            time.sleep(scroll_pause)
    raise Exception("Buton kaydırmalara rağmen bulunamadı.")


def scroll_until_text_found(driver, by, value, max_scrolls=15, scroll_pause=1.5):
    for i in range(max_scrolls):
        try:
            element = driver.find_element(by, value)
            text = element.text.strip()
            if text:
                print(f"{i + 1}. kaydırmada ürün adı bulundu.")
                return text
        except:
            pass
        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.1);")
        time.sleep(scroll_pause)
    raise Exception("Ürün adı kaydırmalara rağmen bulunamadı.")


def search_and_click_on_products(search_term):
    db_config = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432
    }

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://www.trendyol.com")
        close_cookie_consent(driver)

        try:
            search_bar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="sfx-discovery-search-suggestions"]/div/div/input'))
            )
            search_bar.send_keys(search_term)
            search_bar.send_keys(Keys.ENTER)
            print(f"{search_term} için arama yapıldı.")
            time.sleep(3)
        except Exception as e:
            print(f"Arama çubuğu bulunamadı veya işlem başarısız oldu: {e}")

        try:
            product_titles = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'h3.prdct-desc-cntnr-ttl-w'))
            )
            print(f"{len(product_titles)} adet ürün bulundu. Ürünlere tıklanıyor...")

            for index, title in enumerate(product_titles[:2]):
                try:
                    product_element = title.find_element(By.XPATH, "./ancestor::a")
                    product_url = product_element.get_attribute("href")
                    driver.execute_script("window.open(arguments[0]);", product_url)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(3)

                    if index == 0:
                        close_initial_popup(driver)

                    time.sleep(2)

                    try:
                        product_name = scroll_until_text_found(
                            driver,
                            By.XPATH,
                            '//*[@id="envoy"]/div/h1',
                            max_scrolls=15,
                            scroll_pause=1.5
                        )
                        print(f"Ürün Adı: {product_name}")
                    except Exception as e:
                        print(f"Ürün ismi alınamadı: {e}")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue  # ürün adı yoksa yorumlara geçme

                    try:
                        see_all_reviews_button = scroll_until_element_found(
                            driver,
                            By.XPATH,
                            '//*[@id="reviews-container"]/div[3]/a/span',
                            max_scrolls=20,
                            scroll_pause=1.5
                        )
                        see_all_reviews_button.click()
                        time.sleep(2)
                        print("Yorumlar sayfasına yönlendirildi.")
                    except Exception as e:
                        print(f"Tüm yorumlara gitme bağlantısı bulunamadı: {e}")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue

                    reviews = []
                    ratings = []
                    no_new_data_attempts = 0

                    while no_new_data_attempts < 3:
                        new_data_found = False
                        index_review = len(reviews) + 1

                        while True:
                            try:
                                review_xpath = f'//*[@id="rating-and-review-app"]/div/div/div/div[3]/div/div/div[3]/div[2]/div[{index_review}]/div[2]'
                                rating_stars_xpath = f'//*[@id="rating-and-review-app"]/div/div/div/div[3]/div/div/div[3]/div[2]/div[{index_review}]/div[1]/div[1]/div/div'

                                review_element = driver.find_element(By.XPATH, review_xpath)
                                star_elements = driver.find_elements(By.XPATH, rating_stars_xpath)

                                reviews.append(review_element.text)

                                stars = 0
                                for star in star_elements:
                                    try:
                                        full_star = star.find_element(By.XPATH, './div[2]')
                                        style = full_star.get_attribute('style')
                                        width_percentage = int(style.split("width:")[1].split("%")[0].strip())
                                        if width_percentage > 50:
                                            stars += 1
                                    except Exception:
                                        continue

                                ratings.append(stars)
                                index_review += 1
                                new_data_found = True
                            except Exception:
                                break

                        if not new_data_found:
                            current_scroll_position = driver.execute_script("return window.pageYOffset;")
                            page_height = driver.execute_script("return document.body.scrollHeight;")
                            next_scroll_position = current_scroll_position + (page_height * 0.27)
                            driver.execute_script(f"window.scrollTo(0, {next_scroll_position});")
                            time.sleep(2)
                            no_new_data_attempts += 1
                        else:
                            no_new_data_attempts = 0

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

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    print(f"{index + 1}. ürüne tıklanırken hata oluştu: {e}")

        except Exception as e:
            print(f"Ürün başlıkları bulunamadı: {e}")

    finally:
        time.sleep(3)
        driver.quit()


if __name__ == "__main__":
    search_term = input("Aramak istediğiniz kelimeyi girin: ")
    search_and_click_on_products(search_term)
