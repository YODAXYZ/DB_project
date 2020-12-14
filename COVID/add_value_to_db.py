import psycopg2
import logging
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from web_scraping.corona_scraping import *


class DbWorker:
    def __init__(self, df):
        self.df = df
        try:
            self.__conn = psycopg2.connect(dbname='itis_java', user='postgres',
                                           password='postgres', host='localhost')
            self.__conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.__cursor = self.__conn.cursor()
            logging.getLogger().addHandler(logging.StreamHandler())
        except:
            logging.exception("DB connection failed")

    def delete_old_version(self):
        try:
            self.__cursor.execute("""
            drop table country;
            drop table continent;
            """)
        except:
            logging.warning("Country and continent don't exists")

    def create_table(self):
        try:
            self.__cursor.execute("""
            CREATE TABLE Continent
            (
                Id INTEGER PRIMARY KEY,
                Name VARCHAR NOT NULL UNIQUE
            );
        
            CREATE TABLE Country
            (
                Id INTEGER PRIMARY KEY,
                Name VARCHAR,
                NumberOfCases INTEGER,
                Deaths INTEGER,
                ContinentName VARCHAR,
                FOREIGN KEY (ContinentName) REFERENCES Continent (Name)
            );
            """)
        except:
            logging.exception("Create table error !")

    def insert_table(self):
        country = list()
        for i in range(len(self.df)):
            if str(df.iloc[i]["Continent"]) not in country:
                if str(df.iloc[i]["Continent"]).replace(" ", "") != "":
                    country.append(df.iloc[i]['Continent'])
                    try:
                        self.__cursor.execute(f"""
                           INSERT INTO Continent (id, name) VALUES ({i + 1}, '{str(df.iloc[i]["Continent"])}') 
                        """)
                    except:
                        logging.exception("Insert into continent table error !")
        for i in range(len(self.df)):
            postgres_insert_query = """INSERT INTO Country VALUES (%s,%s,%s,%s,%s);"""
            if str(df.iloc[i]["Continent"]).replace(" ", "") != "":
                record_to_insert = (
                    i, str(df.iloc[i]["Country"]), int(df.iloc[i]["Number of cases"]), int(df.iloc[i]["Deaths"]),
                    str(df.iloc[i]["Continent"]))
                try:
                    self.__cursor.execute(postgres_insert_query, record_to_insert)
                except:
                    logging.exception("Insert into country table error !")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__conn.close()


if __name__ == "__main__":
    url_df = 'https://www.worldometers.info/coronavirus/countries-where-coronavirus-has-spread/'
    url_case = 'https://www.worldometers.info/coronavirus/'

    scraping = Scraping(url_df, url_case)
    df = scraping.df_day_statistic()
    db_connect = DbWorker(df)
    db_connect.delete_old_version()
    db_connect.create_table()
    db_connect.insert_table()
