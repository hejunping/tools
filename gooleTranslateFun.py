#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
google 翻译的方法 多进程测试
"""
import requests
from fake_useragent import UserAgent
import re
import execjs
import json
from urllib.parse import urlencode
from multiprocessing import Pool


def get_headers():
    ua = UserAgent()
    headers = {
        'user-agent': ua.random
    }
    return headers

### 获取TKK
def get_tkk():
    url = 'https://translate.google.cn/'
    req = requests.get(url, headers=get_headers())
    tkklist = re.findall("tkk:'(\d+\.\d+)'", req.text)
    if tkklist:
        return tkklist[0]
    else:
        raise ValueError("get tkk error")


# 通过 TKK 和翻译的内容生成 tk
def get_tk(content):
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
    tk = ctx.call('tk', content, get_tkk())
    return tk


# 翻译文本内容
def get_translated(content):
    translate_content = []
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
        "tk": get_tk(content),
        "format": "html"
    }
    url = "%s?%s" % (url, urlencode(parm))
    data = {
        "q": content
    }
    req = requests.post(url, data=data, headers=get_headers())
    translate_content_list = json.loads(req.text)
    for item in translate_content_list[0]:
        if not item[0]:
            break
        translate_content.append(item[0])
    return "\n".join(translate_content)


# 翻译HTML
def get_translate_from_html(content):
    url = "https://translate.googleapis.com/translate_a/t"
    parm = {
        "anno": 3,
        "client": "te_lib",
        "format": "html",
        "v": "1.0",
        "key": "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw",
        "logld": "vTE_20200506_00",
        "sl": "en",
        "tl": "zh-CN",
        "sp": "nmt",
        "tc": 2,
        "sr": 1,
        "tk": get_tk(content),
        "mode": 1
    }
    url = "%s?%s" % (url, urlencode(parm))
    data = {
        "q": content
    }
    req = requests.post(url, data=data, headers=get_headers())
    print(req.json())
    return req.json()


if __name__ == '__main__':
    content = """
    <p>Thanks Google Translate 
    <code>print("hello Google Translate")</code>
    </p>
    <p>20200602</p>
    """
    p = Pool(2)
    for i in range(10):
        p.apply_async(get_translate_from_html, args=(content, ))
    p.close()
    p.join()
    print("done")