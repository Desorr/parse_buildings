import json
import time
import requests
from selenium import webdriver
import os
from buildings_report import BuildingsReport

class Building(webdriver.Chrome):
    def __init__(self, driver_path=r"C:\\Users\\Егор\\.cache\\selenium\\chromedriver\\win64\\109.0.5414.74\\chromedriver.exe", teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ["PATH"] += os.pathsep + self.driver_path

        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-web-security")
        
        super(Building, self).__init__(options=options)
        self.original_wait = 10
        self.implicitly_wait(self.original_wait)
        self.maximize_window()

    def report_results(self):
        report = BuildingsReport(self)
        report.scrape_listings()

def send_webhook(json_file, webhook_url):
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Отправка POST-запроса с данными
        response = requests.post(webhook_url, json=data, headers={"Content-Type": "application/json"})

        # Проверка ответа
        if response.status_code == 200:
            print("Вебхук успешно отправлен!")
        else:
            print(f"Ошибка при отправке вебхука: {response.status_code}, {response.text}")
    except FileNotFoundError:
        print(f"Файл {json_file} не найден.")
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле {json_file}.")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    while True:
        with Building(teardown=True) as bot:
            bot.report_results()

            json_file = "buildings_data.json"
            webhook_url = "https://example.com/webhook"
            send_webhook(json_file, webhook_url)

        print("Задача завершена. Ожидание 3 минуты перед следующим запуском.")
        time.sleep(180)