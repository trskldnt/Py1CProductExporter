import argparse
import os
import sys
import logging
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException
import time

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Разбор аргументов командной строки
parser = argparse.ArgumentParser(description="Автоматизация загрузки файла на сайт Avtopto.")
parser.add_argument('--login', help="Логин пользователя", required=True)
parser.add_argument('--password', help="Пароль пользователя", required=True)
parser.add_argument('--file', help="Имя файла для загрузки", required=True)
parser.add_argument('--wh', help="Номер склада", required=True)
args = parser.parse_args()

login = args.login
password = args.password
warehouse_number = args.wh
warehouse_url = "https://avto.pro/warehouses/" + warehouse_number
file_name = args.file
file_path = os.path.join(os.getcwd(), file_name)

# Проверка на существование файла
if not os.path.exists(file_path):
    logging.error(f"Файл {file_name} не найден. Проверьте правильность пути.")
    sys.exit(1)


try:
    driver = uc.Chrome(use_subprocess=False)
    driver.get('https://avto.pro')

    # Попытка найти и нажать на кнопку cookie
    try:
        cookie_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#cookie-block > form > button")))
        cookie_button.click()
        logging.info("Кнопка cookie обработана.")
    except (NoSuchElementException,TimeoutException):
        logging.info("Кнопка cookie не найдена. Продолжаем.")

    # Ввод данных для входа
    try:
        text_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#auth-form-container > div.auth__section > form > div.auth__form__fieldset > div:nth-child(1) > div > input')))
        text_field.send_keys(login)
        text_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#auth-form-container > div.auth__section > form > div.auth__form__fieldset > div:nth-child(2) > div > input')))
        text_field.send_keys(password)
        logging.info("Данные для входа введены.")
    except Exception as e:
        logging.error(f"Ошибка при вводе данных для входа: {e}")
        sys.exit(1)

    # Вход в систему
    try:
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#auth-form-container > div.auth__section > form > div.auth__form__footer > div > button")))
        button.click()
        logging.info("Вход в систему выполнен.")
    except Exception as e:
        logging.error(f"Ошибка при попытке входа в систему: {e}")
        sys.exit(1)

    try:
        driver.get(warehouse_url)
        driver.get(warehouse_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Пример ожидания загрузки элемента
        logging.info("Страница склада успешно загружена.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке страницы: {e}")
        sys.exit(1)


    try:
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#wh-app-container > section > div > div.add-parts > div:nth-child(2) > button")))
        button.click()
        logging.info("Переход на страницу загрузки прайса")
    except Exception as e:
        logging.error(f"Переход на страницу загрузки прайса: {e}")
        sys.exit(1)


    
    # Попытка найти и нажать на кнопку cookie
    try:
        cookie_button = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn-cancelpriceuploading")))
        cookie_button.click()
        logging.info("Отмена незавершенной загрузки прайса.")
        try:
            # Переключение на всплывающее окно
            alert = WebDriverWait(driver, 10).until(EC.alert_is_present())

            # Получение текста из всплывающего окна (если необходимо)
            alert_text = alert.text
            logging.info(f"Текст всплывающего окна: {alert_text}")

            # Подтверждение всплывающего окна (нажатие 'OK')
            alert.accept()
            logging.info("Всплывающее окно подтверждено.")

        except NoAlertPresentException:
            logging.info("Всплывающее окно не появилось.")        

        try:
            button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#wh-app-container > section > div > div.add-parts > div:nth-child(2) > button")))
            button.click()
            logging.info("Переход на страницу загрузки прайса2")
        except Exception as e:
            logging.error(f"Переход на страницу загрузки прайса2: {e}")
            sys.exit(1)
    except Exception as e:
        logging.info(f"незавершенной загрузки прайса не найдена. Продолжаем.")


    # Загрузка файла
    try:
        file_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#input_load_price")))
        file_input.send_keys(file_path)
        driver.find_element(By.CSS_SELECTOR, "#changePositionForm > div > button").click()
        logging.info("Файл загружен.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла: {e}")
        sys.exit(1)

    # Завершение процесса
    try:
        WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#reg > div.panel.panel-danger > div.panel-footer.flex.vertical.align-center > form > div > button"))).click()
        logging.info("Процесс завершен успешно.")
    except Exception as e:
        logging.error(f"Ошибка при завершении процесса: {e}")
        sys.exit(1)


    try:
        # Объединение селекторов
        selector = "#pricelisractions > fieldset > label.checkbox.mb-x1 > input[type=checkbox], #pricelisractions > fieldset > label.checkbox.mb-x2 > input[type=checkbox]"
        
        # Ожидание, пока чекбоксы станут доступны для взаимодействия
        checkboxes = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))

        for checkbox in checkboxes:
            if not checkbox.is_selected():
                checkbox.click()
                logging.info("Чекбокс отмечен.")

        logging.info(f"Все чекбоксы отмечены. Всего отмечено {len(checkboxes)} чекбоксов.")

    except Exception as e:
        logging.error(f"Ошибка при отмечании чекбоксов: {e}")
        sys.exit(1)

    
    try:
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#pricelisractions > fieldset > button")))
        button.click()
        logging.info("Кнопка Загрузить запчасти на склад")
    except Exception as e:
        logging.error(f"Ошибка кнопки Загрузить запчасти на склад: {e}")
        sys.exit(1)

    logging.info("Загрузка прайса на Автопро завершена")
    time.sleep(3)
    # WebDriverWait(driver, 200).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "reg > div.panel.panel-danger > div.panel-footer.flex.vertical.align-center > form > div > button"))).click()

except Exception as e:
    exception_type = type(e).__name__  # Получение имени типа исключения
    logging.error(f"Произошло исключение: {exception_type}, Сообщение: {e}")
    sys.exit(1)
finally:
    driver.quit()
