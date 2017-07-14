# -*- coding: utf-8 -*-

from wox import Wox, WoxAPI
import webbrowser


class Qb(Wox):
    def query(self, query):
        que = query.split()
        results = [{
            "Title": "Go to Exchange",
            "SubTitle": "Please input valid exhcnage and coin",
            "IcoPath": "Images/app.ico",
        }]
        if len(que) != 2:
            return results
        exchange = que[0].lower()
        coin = que[1].lower()
        if exchange == 'yunbi':
            url = f"https://yunbi.com/markets/{coin}cny"
        elif exchange == 'jubi':
            url = f"https://www.jubi.com/coin/{coin}/"
        else:
            return results
        results = [{
            "Title": "Go to Exchange",
            "SubTitle": f"go to {exchange}'s {coin}",
            "IcoPath": "Images/app.ico",
            "JsonRPCAction": {
                "method": "openUrl",
                "parameters": [url],
                "dontHideAfterAction": False
            }
        }]
        return results

    def openUrl(self, url):
        webbrowser.open(url)
        WoxAPI.change_query("")


if __name__ == "__main__":
    Qb()
