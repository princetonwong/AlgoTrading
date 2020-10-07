from lxml import html
import requests
import json
from collections import OrderedDict
import pandas as pd
from tqdm.contrib.concurrent import process_map
import os
from CustomAPI.Helper import Helper
from datetime import datetime

class YahooScraper():

    @staticmethod
    def turnSuffixToFloat(series):
        series = [str(x) for x in series]
        m = {'K': 3, 'M': 6, 'B': 9, 'T': 12}
        k = [float(i[:-1]) * 10 ** m[i[-1]] / 1000 for i in series]
        return k

    @staticmethod
    def turnStringToFloat(df):
        s = ["Previous Close", "Open", "Volume", "Avg. Volume"]
        f = lambda x: float(x.replace(',', ''))
        for i in s:
            df[i] = df[i].apply(f)

    @staticmethod
    def getHeaders():
        return {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
                "cache-control": "max-age=0",
                "dnt": "1",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}

    @staticmethod
    def get_tickers_from_wikipedia():
        '''
        Get list of S&P 500 components from Wikipedia
        '''
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies#S&P_500_Component_Stocks'
        l = pd.read_html(url)
        # store the result in a dataframe - you only need the first element, the table
        output = pd.DataFrame(l[0])

        print(output)
        return output["Symbol"]

        # # keep only columns: Security Symbol and GICS Sector
        # output = output.drop(columns=[2, 4, 5, 6, 7, 8], axis=1)
        # output = output[[1, 0, 3]] # swap order of ticker and company name
        # output.to_csv(save_to, sep=',', encoding='utf-8',index=True)

    def parse(self, ticker):
        ticker = ticker["SYMBOL"]
        url = "http://finance.yahoo.com/quote/%s?p=%s" % (ticker, ticker)
        response = requests.get(
            url, verify=False, headers=self.getHeaders(), timeout=30)
        print("Parsing %s" % (url))
        parser = html.fromstring(response.text)
        summary_table = parser.xpath(
            '//div[contains(@data-test,"summary-table")]//tr')
        summary_data = OrderedDict()
        other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(
            ticker)
        summary_json_response = requests.get(other_details_json_link)
        try:
            json_loaded_summary = json.loads(summary_json_response.text)
            summary = json_loaded_summary["quoteSummary"]["result"][0]
            y_Target_Est = summary["financialData"]["targetMeanPrice"]['raw']
            earnings_list = summary["calendarEvents"]['earnings']
            eps = summary["defaultKeyStatistics"]["trailingEps"]['raw']
            datelist = []

            for i in earnings_list['earningsDate']:
                datelist.append(i['fmt'])
            earnings_date = ' to '.join(datelist)

            for table_data in summary_table:
                raw_table_key = table_data.xpath(
                    './/td[1]//text()')
                raw_table_value = table_data.xpath(
                    './/td[2]//text()')
                table_key = ''.join(raw_table_key).strip()
                table_value = ''.join(raw_table_value).strip()
                summary_data.update({table_key: table_value})
            summary_data.update({'1y Target Est': y_Target_Est, 'EPS (TTM)': eps,
                                 'Earnings Date': earnings_date, 'ticker': ticker,
                                 'url': url})
            # summary_data = pd.DataFrame(list(summary_data.values()), index=summary_data.keys()).T

            return summary_data

        except ValueError:
            print("Failed to parse json response")
            return {"error": "Failed to parse json response"}
        except:
            return {"error": "Unhandled Error"}


    def dailySP500Scrap(self, sortKey: str = "Market Cap") -> pd.DataFrame:
        all_list = []
        symbols = self.get_tickers_from_wikipedia()
        for symbol in symbols:
            allParams = dict(SYMBOL= symbol)
            all_list.append({**allParams})

        stats = process_map(self.parse, all_list, max_workers=os.cpu_count())

        df = pd.DataFrame(stats)
        df = df[df["error"] != "Unhandled Error"]
        df["Market Cap"] = self.turnSuffixToFloat(df["Market Cap"])
        self.turnStringToFloat(df)
        df.sort_values(sortKey, ascending=False, inplace=True)
        df= df.reset_index(drop=True)
        # Helper().gradientAppliedXLSX(df, "SP500 - " + datetime.now().strftime("%Y-%m-%d"), [])
        Helper().gradientAppliedXLSX(df, "SP500", [])
        return df