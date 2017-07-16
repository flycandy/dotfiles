# -*- coding: utf-8 -*-

from wox import Wox, WoxAPI
import requests
import json
import webbrowser


class Qb(Wox):
    def query(self, query):
        que = query.split()
        results = [{
            "Title": "Quote",
            "SubTitle": "You can get lastest coin quote",
            "IcoPath": "Images/app.ico",
        }]
        if len(que) == 1:
            que = que[0]
            if que in ['btc', 'eth', 'ltc']:
                res = requests.get(f'http://api.qbtrade.org/redis/get?key=tick.v2:{que}:exchange.xtc.okcn')
                value = json.loads(json.loads(res.text)['value'])
                results = [{
                    "Title": "Quote",
                    "SubTitle": f"{que} last:{value['last']} bid1:{value['bids'][0]['price']} ask1:{value['asks'][0]['price']}",
                    "IcoPath": "Images/app.ico",
                }]
                return results
        return results


if __name__ == "__main__":
    Qb()
