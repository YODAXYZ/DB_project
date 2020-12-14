import smtplib
import time
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Coronavirus:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome("/Users/aleksandr/Desktop/Programm/python/Univer/term_3/DB_project/chromedriver",
                                       options=options)  # change location to chromedriver


def send_email(data, email):
    total_cases = data[2]
    new_cases = data[3]
    total_deaths = data[4]
    new_deaths = data[5]
    active_cases = data[6]
    total_recovered = data[7]
    serious_critical = data[8]

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('<your_login>', '<your_pas>')  # and also you need take permission to connect
    # to your mail (it's in privacy poly in gmail)
    subject = 'Coronavirus stats in your country today!'

    body = f"""
            Today in {country_element.text}
            There is new data on coronavirus:
            Total cases: {total_cases}
            New cases: {new_cases}
            Total deaths: {total_deaths}
            New deaths: {new_deaths}
            Active cases: {active_cases}
            Total recovered: {total_recovered}
            Serious, critical cases: {serious_critical}
            """
    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail(
        'CoronaVirusStatistic',
        email,
        msg
    )
    server.quit()


if __name__ == "__main__":
    bot = Coronavirus()
    bot.driver.get('https://www.worldometers.info/coronavirus/')
    time.sleep(3)
    table = bot.driver.find_element_by_xpath('//*[@id="main_table_countries_today"]/tbody[1]')

    country_element = table.find_element_by_xpath("//td[contains(., 'Russia')]")

    row = country_element.find_element_by_xpath("./..")

    data = row.text.split(" ")
    email = sys.argv[1]
    send_email(data, email)


