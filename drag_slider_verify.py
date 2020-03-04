#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小鹅通登录
"""
from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import random
import logging
import os
import requests
import cv2
import numpy as np

class MoveCaptcha:
    lg = None
    driver = None
    user_name = None
    password = None
    distance = 180
    evn = None
    path = None

    def __init__(self, user_name, password, evn=''):
        self.user_name = user_name
        self.password = password
        self.evn = evn
        self.set_log(evn)
        if self.evn == 'test':
            self.lg.info("测试环境开始...")
        else:
            self.lg.info("正式环境开始...")

    def set_log(self, evn):
        if evn == 'test':
            self.path = '%s' % os.path.abspath(os.path.dirname(__file__))
        else:
            self.path = '/home/admin/pyspider/checked'
        self.lg = logging.getLogger('move_code')
        self.lg.setLevel(level=logging.INFO)
        if not self.lg.handlers:
            fh = logging.FileHandler("%s/move_code.log" % self.path)
            fh.setLevel(level=logging.INFO)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'))
            self.lg.addHandler(fh)


    def get_track(self, distance):
        '''
        拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速
        匀变速运动基本公式：
        ①v=v0+at
        ②s=v0t+(1/2)at²
        ③v²-v0²=2as

        :param distance: 需要移动的距离
        :return: 存放每0.2秒移动的距离
        '''
        # 初速度
        v=0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t=0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks=[]
        # 当前的位移
        current=0
        # 到达mid值开始减速
        mid=distance * 7/8

        distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(2,4)  # 加速运动
            else:
                a = -random.randint(3,5) # 减速运动

            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0*t+0.5*a*(t**2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))

            # 速度已经达到v,该速度作为下次的初速度
            v= v0+a*t

        # 反着滑动到大概准确位置
        for i in range(4):
           tracks.append(-random.randint(2, 3))
        for i in range(4):
           tracks.append(-random.randint(1, 3))
        return tracks

    def move_to_gap(self, driver):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        iframe = driver.find_element_by_tag_name("iframe")
        driver.switch_to.frame(iframe)
        move_bnt = driver.find_element_by_id("slideBlock")
        idx = 0
        while 1:
            idx = idx + 1
            self.distance = self.get_image_position()
            self.lg.info("移动距离:%s" % self.distance)
            time.sleep(1)
            self.lg.info("第%s次开始" % idx)
            time.sleep(3)
            track = self.get_track(self.distance)
            self.lg.info("点击滑动按钮")
            ActionChains(driver).click_and_hold(move_bnt).perform()
            time.sleep(1)
            self.lg.info("拖动元素")
            for x in track:
                ActionChains(driver).move_by_offset(x, 0).perform()
            time.sleep(0.5)
            self.lg.info("释放鼠标")
            ActionChains(driver).release().perform()
            time.sleep(1)
            self.lg.info('滑动轨迹')
            tcaptcha_cover_success = driver.find_element_by_id("tcaptcha_cover_success")
            success_txt = tcaptcha_cover_success.get_attribute('innerText')
            if success_txt:
                self.lg.info(success_txt)
                break
            self.lg.info("失败重新刷新")
            reload_bnt = driver.find_element_by_id("e_reload")
            ActionChains(driver).click(reload_bnt).perform()
            time.sleep(1)

    def create_chorme(self):
        """
        创建浏览器访问
        :return:
        """
        if self.evn == 'test':
            self.driver = webdriver.Chrome(executable_path='/Users/rick/tools/chromedriver')
        else:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            self.driver = webdriver.Chrome(executable_path='/opt/drivers/chromedriver', chrome_options=chrome_options)
        self.driver.get('https://admin.xiaoe-tech.com/login_page?xeuti=ituex#/acount')
        logging.info(self.driver.title)
        login_btn = self.driver.find_element_by_class_name("login-btn")
        user = self.driver.find_element_by_xpath("//div[@class='phoneWrapper']/div[@class='inputBox']/input")
        password = self.driver.find_element_by_xpath("//div[@class='passwordWrapper']/div[@class='inputBox']/input")
        user.send_keys(self.user_name)
        password.send_keys(self.password)
        ActionChains(self.driver).move_to_element(login_btn).click(login_btn).perform()
        time.sleep(2)
        self.move_to_gap(self.driver)
        time.sleep(5)
        self.lg.info("选择店铺")
        self.driver.get("https://admin.xiaoe-tech.com/muti_index#/chooseShop")
        choose_shop = self.driver.find_element_by_class_name("shop-list-item__active")
        ActionChains(self.driver).click(choose_shop).perform()
        time.sleep(5)

    def get_cookie(self, key=None):
        """
        获取cookies
        :return:
        """
        self.lg.info("获取 Token")
        if key:
            cookie_value = self.driver.get_cookie(key).get('value')
        else:
            tmplist = {}
            for item in self.driver.get_cookies():
                tmplist[item['name']] = item['value']
            cookie_value = tmplist
        # self.driver.close()
        self.driver.quit()
        self.lg.info(cookie_value)
        return cookie_value

    def get_image_position(self):
        image1 = self.driver.find_element_by_id('slideBkg').get_attribute('src')
        image2 = self.driver.find_element_by_id('slideBlock').get_attribute('src')

        if image1 == None or image2 == None:
            return

        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0'

        req =requests.get(image1, headers={'User-Agent': ua})
        f = open('%s/slide_bkg.png' % self.path, 'wb')
        f.write(req.content)
        f.close()

        req = requests.get(image2, headers={'User-Agent': ua})
        f = open('%s/slide_block.png' % self.path, 'wb')
        f.write(req.content)
        f.close()

        block = cv2.imread('%s/slide_block.png' % self.path, 0)
        template = cv2.imread('%s/slide_bkg.png' % self.path, 0)

        cv2.imwrite('%s/template.jpg' % self.path, template)
        cv2.imwrite('%s/block.jpg' % self.path, block)
        block = cv2.imread('%s/block.jpg' % self.path)
        block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
        block = abs(255 - block)
        cv2.imwrite('%s/block.jpg' % self.path, block)

        block = cv2.imread('%s/block.jpg' % self.path)
        template = cv2.imread('%s/template.jpg' % self.path)

        result = cv2.matchTemplate(block, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)
        return int(y * 0.4)


if __name__ == '__main__':
    mc = MoveCaptcha("13xxxxxxxxx", "*******", "test")
    mc.create_chorme()
    mc.get_cookie('b_user_token')



