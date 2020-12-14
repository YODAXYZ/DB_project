import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
from matplotlib.pyplot import figure
from bs4 import BeautifulSoup


class Scraping:
    def __init__(self, url_for_df, url_for_case):
        self.url_for_df = url_for_df
        self.url_for_case = url_for_case
        self.time = datetime.date.today()

    def df_day_statistic(self):
        page = requests.get(self.url_for_df)
        soup = BeautifulSoup(page.text, 'html.parser')

        data = []

        data_iterator = iter(soup.find_all('td'))

        while True:
            try:
                country = next(data_iterator).text
                confirmed = next(data_iterator).text
                deaths = next(data_iterator).text
                continent = next(data_iterator).text

                # For 'confirmed' and 'deaths', make sure to remove the commas and convert to int
                data.append((
                    country,
                    (int(confirmed.replace(',', ''))),
                    (int(deaths.replace(',', ''))),
                    continent
                ))
                # StopIteration error is raised when there are no more elements left to iterate through
            except StopIteration:
                break

        data.sort(key=lambda row: row[1], reverse=True)

        df = pd.DataFrame(data, columns=['Country', 'Number of cases', 'Deaths', 'Continent'], dtype=float)
        df_corona = df.sort_values(by='Number of cases', ascending=False)

        # df_corona['Death_rate'] = (df['Deaths'] / df['Number of cases']) * 100
        return df_corona

    def generic_case(self):
        page = requests.get(self.url_for_case)
        soup = BeautifulSoup(page.text, 'html.parser')
        case = {'case': soup.select('#maincounter-wrap>div>span')[0].text,
                'death': soup.select('#maincounter-wrap>div>span')[1].text,
                'recover': soup.select('#maincounter-wrap>div>span')[2].text}

        return case
    
    def save_generic_case(self):
        page = requests.get(self.url_for_case)
        soup = BeautifulSoup(page.text, 'html.parser')
        case = f"Case: {soup.select('#maincounter-wrap>div>span')[0].text} \n" \
               f"Death: {soup.select('#maincounter-wrap>div>span')[1].text} \n" \
               f"Recovery: {soup.select('#maincounter-wrap>div>span')[2].text}" 
        
        with open(f"COVID_data/{self.time}.txt", "w") as f:
            f.write(case)

    def save_file(self):
        df = self.df_day_statistic()
        df.to_csv(f"COVID_data/{self.time}", header=False, index=False)


def death_rate(df_corona):
    figure(num=None, figsize=(20, 6), dpi=80, facecolor='w', edgecolor='k')
    df_corona = df_corona[~df_corona.Continent.isin([''])]
    sns.barplot(x='Continent', y='Death_rate', data=df_corona.sort_values(by='Death_rate', ascending=False))
    plt.show()


def main_statistic_contint(df_corona):
    figure(num=None, figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')
    sns_plot = sns.pairplot(df_corona, hue='Continent')
    figure_plot = sns_plot
    figure_plot.savefig("COVID_data/FullStat.png")
    # plt.show()


def case_statistic(df_corona):
    figure(num=None, figsize=(10, 10),  facecolor='w', edgecolor='k')
    sns_plot = sns.barplot(x='Country', y='Number of cases', data=df_corona.head(10))
    figure_plot = sns_plot.get_figure()
    figure_plot.savefig("COVID_data/CaseStat.png")
    # plt.show()


if __name__ == "__main__":
    url_df = 'https://www.worldometers.info/coronavirus/countries-where-coronavirus-has-spread/'
    url_case = 'https://www.worldometers.info/coronavirus/'

    scraping = Scraping(url_df, url_case)
    df = scraping.df_day_statistic()
    scraping.save_file()
    case_statistic(df)
    main_statistic_contint(df)
    scraping.save_generic_case()
    print(scraping.generic_case())

