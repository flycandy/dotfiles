# -*- coding: utf-8 -*-

from wox import Wox, WoxAPI
import webbrowser
import os


class Qb(Wox):
    def query(self, query):
        que = query.split()
        friend = que[0]
        results = [{
            "Title": "Call WeChat",
            "SubTitle": f"call {friend}",
            "IcoPath": "Images/app.png",
            "JsonRPCAction": {
                "method": "callwechat",
                "parameters": [friend],
                "dontHideAfterAction": False
            }
        }]
        return results

    def callwechat(self, friend):
        os.system(f'start wechatcall.ahk {friend}')
        WoxAPI.change_query("")


if __name__ == "__main__":
    Qb()
