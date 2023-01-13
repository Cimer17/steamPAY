# для создания профиля фаерфокс ежедневный запуск
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from aiogram import Bot
from selenium.webdriver.common.by import By
import time
import os
import shutil
import asyncio
import configparser
import sys_const
import schedule
from sys_const import profile

config = configparser.ConfigParser()
config.read(sys_const.settings, encoding="utf-8")
token = config["notifications_steam"]["tokens"]
group_id = config["notifications_steam"]["group_id"]
telephone = config["QIWI"]["telephone"]
password_qiwi = config["QIWI"]["password"]
PATH_TO_DEV_NULL = 'nul'
bot = Bot(token=token)

async def notifications_steam(mes):
    await bot.send_message(group_id, mes)

def new_profile():
    try:
        os.mkdir('cash')
        options = Options()
        options.headless = True
        options.add_argument('-profile')
        options.add_argument(profile)
        driver = webdriver.Firefox(options=options,
                                executable_path='geckodriver.exe',
                                service_args=['--marionette-port', '2828'],
                                service_log_path=PATH_TO_DEV_NULL)
        driver.get("https://qiwi.com/payment/form/31212")
        print('Авторизовываюсь...')
        time.sleep(5)
        driver.find_element(By.XPATH, '/html/body/div[2]/section/div/div[1]/header/div[1]/div/div/div[2]/button').click()
        time.sleep(2)
        login = driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div[2]/form/div[2]/div[1]/div/div[2]/div/input')
        login.send_keys(telephone)
        time.sleep(2)
        password = driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div[2]/form/div[2]/div[2]/div/div[2]/input')
        password.send_keys(password_qiwi)
        time.sleep(2)
        driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/div[2]/form/div[2]/div[3]/div/div/button/span/span').click()
        print('Успешная авторизация!')
        time.sleep(2)
        # для винды asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(notifications_steam('Авторизация прошла успешно'))
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

def update_profile():
    print('Обновляю профиль...')
    shutil.rmtree('cash')
    new_profile()
    print('Обновил профиль...')

schedule.every().day.at('00:15').do(update_profile)
while 1:
    schedule.run_pending()
    time.sleep(1)