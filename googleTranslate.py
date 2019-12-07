#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
google 翻译
"""
import requests
from fake_useragent import UserAgent
import re
import execjs
import json
import urllib


class GoogleTranslate:
    content = ""

    def __init__(self):
        ua = UserAgent()
        self.headers = {
            'user-agent': ua.random
        }

    # 从页面中获取 TKK值
    def get_TKK(self):
        url = 'https://translate.google.cn/'
        req = requests.get(url, headers=self.headers)
        tkklist = re.findall("tkk:'(\d+\.\d+)'", req.text)
        if tkklist:
            return tkklist[0]
        else:
            print u"get tkk error"
            exit()

    # 通过 TKK 和翻译的内容生成 tk
    def get_tk(self):
        js = """
        var b = function (a, b) {
            for (var d = 0; d < b.length - 2; d += 3) {
                var c = b.charAt(d + 2),
                    c = "a" <= c ? c.charCodeAt(0) - 87 : Number(c),
                    c = "+" == b.charAt(d + 1) ? a >>> c : a << c;
                a = "+" == b.charAt(d) ? a + c & 4294967295 : a ^ c
            }
            return a
        }
        var tk =  function (a,TKK) {
            for (var e = TKK.split("."), h = Number(e[0]) || 0, g = [], d = 0, f = 0; f < a.length; f++) {
                var c = a.charCodeAt(f);
                128 > c ? g[d++] = c : (2048 > c ? g[d++] = c >> 6 | 192 : (55296 == (c & 64512) && f + 1 < a.length && 56320 == (a.charCodeAt(f + 1) & 64512) ? (c = 65536 + ((c & 1023) << 10) + (a.charCodeAt(++f) & 1023), g[d++] = c >> 18 | 240, g[d++] = c >> 12 & 63 | 128) : g[d++] = c >> 12 | 224, g[d++] = c >> 6 & 63 | 128), g[d++] = c & 63 | 128)
            }
            a = h;
            for (d = 0; d < g.length; d++) a += g[d], a = b(a, "+-a^+6");
            a = b(a, "+-3^+b+-f");
            a ^= Number(e[1]) || 0;
            0 > a && (a = (a & 2147483647) + 2147483648);
            a %= 1E6;
            return a.toString() + "." + (a ^ h)
        }
        """
        ctx = execjs.compile(js)
        tk = ctx.call('tk', self.content, self.get_TKK())
        return tk

    # 获取翻译内容
    def get_translated(self):
        translate_content = []
        tk = self.get_tk()
        url = "https://translate.google.cn/translate_a/single"
        parm = {
            "client": "webapp",
            "sl": "en",     # 指定要翻译的语言
            "tl": "zh-CN",  # 翻译成的语言
            "hl": "zh-CN",
            "dt": "at",
            "dt": "bd",
            "dt": "ex",
            "dt": "ld",
            "dt": "md",
            "dt": "qca",
            "dt": "rw",
            "dt": "rm",
            "dt": "ss",
            "dt": "t",
            "pc": "1",
            "otf": "2",
            "ssel": "0",
            "tsel": "0",
            "kc": "3",
            "tk": tk,
            # "format": "html"
        }
        url = "%s?%s" % (url, urllib.urlencode(parm))
        data = {
            "q": self.content
        }
        req = requests.post(url, data=data, headers=self.headers)
        translate_content_list = json.loads(req.text)
        for item in translate_content_list[0]:
            if not item[0]:
                break
            translate_content.append(item[0])
        return "\n".join(translate_content)


if __name__ == '__main__':
    gt = GoogleTranslate()
    gt.content = """
    what a wonderful day! 
    """""
    print (gt.get_translated())