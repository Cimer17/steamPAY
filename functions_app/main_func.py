from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import uuid
import configparser
from sys_const import *

config = configparser.ConfigParser()
config.read(settings, encoding="utf-8")
secret_key = config["QIWI"]["secret_key"]
publick_key = config["QIWI"]["publick_key"]
telephone = config["QIWI"]["telephone"]
token = config["QIWI"]["token"]
code_currencies = config["QIWI"]["code_currencies"]
password = config["QIWI"]["password"]
PATH_TO_DEV_NULL = 'nul'

# Конвертация в QIWI Кошельке
def convert_to_tenge(api_access_token, sum_exchange, to_qw):
    s = requests.Session()
    s.headers = {'content-type': 'application/json'}
    s.headers['authorization'] = 'Bearer ' + api_access_token
    s.headers['User-Agent'] = 'Android v3.2.0 MKT'
    s.headers['Accept'] = 'application/json'
    postjson = {"id":"","sum":{"amount":"","currency":""},"paymentMethod":{"type":"Account","accountId":"643"}, "comment":"'+comment+'","fields":{"account":""}}
    postjson['id'] = str(int(time.time() * 1000))
    postjson['sum']['amount'] = sum_exchange
    postjson['sum']['currency'] = code_currencies
    postjson['fields']['account'] = to_qw
    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/1099/payments', json = postjson)
    return res.json()

# Получение курса монет
def curse(api_access_token, currency_to, currency_from):
    s = requests.Session()
    s.headers = {'content-type': 'application/json'}
    s.headers['authorization'] = 'Bearer ' + api_access_token
    s.headers['User-Agent'] = 'Android v3.2.0 MKT'
    s.headers['Accept'] = 'application/json'
    res = s.get('https://edge.qiwi.com/sinap/crossRates')
    rates = res.json()['result']
    rate = [x for x in rates if x['from'] == currency_from and x['to'] == currency_to]
    if (len(rate) == 0):
        print('No rate for this currencies!')
        return
    else:
        return rate[0]['rate']

# проверка платежа
def check_P2P(secret_key, billId):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + secret_key
    s.headers['Accept'] = 'application/json'
    res = s.get(f'https://api.qiwi.com/partner/bill/v1/bills/{billId}')
    try:
        return res.json()['status']['value']
    except KeyError:
        return None

# Отправка денег в стим
def start_steam(login_steam, money):
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(webdriver.FirefoxProfile(profile),options=options, service_log_path=PATH_TO_DEV_NULL)
    driver.set_window_size(1200, 1200)
    url = "https://qiwi.com/payment/form/31212"
    try:
        print('Авторизовываюсь...')
        driver.get(url=url)
        time.sleep(5)
        login_steam_input = driver.find_element(By.XPATH, '//*[@id="app"]/section/section/div[2]/div/div[2]/div/form/div[2]/div/div/div/div/div[1]/div/div[2]/input')
        login_steam_input.clear()
        login_steam_input.send_keys(login_steam)
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="app"]/section/section/div[2]/div/div[2]/div/form/div[2]/div/div/div/div/div[3]/div/div[1]').click()
        print('Ввожу данные steam...')
        time.sleep(5)
        money_input = driver.find_element(By.XPATH,'//*[@id="app"]/section/section/div[2]/div/div[2]/div/form/div[3]/div[2]/div[3]/div/div/div/div[2]/input')
        money_input.clear()
        money_input.send_keys(money)
        print('Ввел сумму, пытаюсь отправить...')
        time.sleep(5)
        driver.find_element(By.XPATH, '/html/body/div[2]/section/section/div[2]/div/div[2]/div/form/div[3]/div[2]/div[5]/div/div/div[1]/button/span/span').click()
        print('Отправляю перевод')
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="app"]/section/section/div[2]/div/div[2]/div/form/div[3]/div/div/div[1]/button/span').click()
        time.sleep(5)
        print('Деньги уже на вашем счету...')
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

# генератор номера заказа
def generator_billId():
    return f'{uuid.uuid4()}'