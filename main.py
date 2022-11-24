import logging
import requests
import pandas as pd
import lxml
from datetime import datetime

from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types

df = pd.read_csv('fin.csv')

API_TOKEN = 'мой токен'

logging.basicConfig(level=logging.INFO)


weekBot = int(((datetime.now() - datetime(datetime.now().year, 9, 1))/7).days + 1)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply('Расписание вузика\nДля получения расписания введите номер своей группе в формате "ПМ-2201"')

@dp.message_handler(commands=["week"])
async def rasweek(message: types.Message):

        args = (message.text).split()

        a = df.index[df['group'] == args[1]].tolist()[0]
        mess = df.iloc[a, 1]

        ans = ""
        for week in range(weekBot, weekBot+1):
            req = requests.get(f"https://rasp.unecon.ru/raspisanie_grp.php?g={mess}&w={week}")

            soup = BeautifulSoup(req.text, "lxml")
            new_days = soup.find_all('tr', class_="new_day")

            data = {}

            for new_day in new_days:

                date = new_day.find('span', class_='date').text
                time = new_day.find("span", class_="time").text
                aud = new_day.find("span", class_="aud").text
                prepod = new_day.find("span", class_="prepod").text
                predmet = new_day.find("span", class_="predmet").text


                if (prepod == ""):
                    ans += "\n📅 " + date + "\n\n⏰" + time + aud + predmet
                else:
                    ans += "\n📅 " + date + "\n\n⏰" + time + aud + predmet + "\n" + prepod


                data[date] = [time, aud, prepod]

                while True:

                    new_day = new_day.find_next_sibling('tr')

                    if new_day['class'] == ['new_day_border']:
                        ans += "\n\n"
                        break

                    time = new_day.find("span", class_="time").text
                    aud = new_day.find("span", class_="aud").text
                    prepod = new_day.find("span", class_="prepod").text
                    predmet = new_day.find("span", class_="predmet").text

                    ans += "\n\n⏰" + time + aud + predmet + "\n" + prepod

                    data[date] += [time, aud, prepod]
        await message.reply(ans)

@dp.message_handler(commands=["day"])
async def rasweek(message: types.Message):
    await message.reply(message.text)

    await message.reply("Расписание на день")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
