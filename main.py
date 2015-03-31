#-*- coding:utf8 -*-
import cv2
import numpy as np
import os
import sys
import mail
import ctypes
import threading
from time import sleep
from pprint import pprint
from random import random
from operator import itemgetter
from itertools import groupby
from proxy_server import *
from winmouse import winMouse
from winscreenshot import screenshot, get_region
import pythoncom
import pyHook
import win32api
import win32con
import win32process

mouse = winMouse()
dir_name = os.getcwd()
sys.path.append(dir_name + os.sep + "img")

if len(sys.argv) > 1:
    argv = sys.argv[1]
else:
    argv = ''

RED = [32, 32, 255]
GREEN = [32, 200, 64]
GRAY = [68, 68, 68]

POS_ATTACK = (196, 266)
POS_BACK = (510, 242)
POS_1_5 = (705, 250)
POS_GO = (660, 445)
POS_SUPPLY = (77, 222)
POS_SUPPLY1 = (117, 117)
POS_SUPPLY2 = (700, 440)
POS_MAIN = (50, 50)
POS_NIGHT = (290, 240)

POS_STAGE_2 = (235, 440)
POS_SORTIE_1 = (285, 200)
POS_SORTIE_2 = (625, 200)
POS_SORTIE_3 = (285, 350)
POS_SORTIE_4 = (625, 350)
POS_SORTIE = [POS_SORTIE_1, POS_SORTIE_2, POS_SORTIE_3, POS_SORTIE_4]

POS_EXP_TEAM_2 = (395, 120)
POS_EXP_TEAM_3 = (425, 120)
POS_EXP_TEAM_4 = (455, 120)
POS_EXP_TEAM = [(395 + 30 * i, 120) for i in xrange(3)]

POS_EXP_2 = (200, 200)  # 2
POS_EXP_5 = (200, 290)  # 5
POS_EXP_6 = (200, 325)  # 6
POS_EXP_STAGE_3 = (260, 440)  # _3
# POS_EXP_21	=	(200,235) #3

POS_EXP_MISSION = [(200, 170 + i * 30) for i in xrange(8)]
POS_EXP_STAGE = [(140 + 60 * i, 440)for i in xrange(5)]

# POS_EXP_21	=	(200,200) #2

POS_GO_EXP = (680, 220)


POS_SUP2 = (180, 120)
POS_SUP3 = (210, 120)
POS_SUP4 = (240, 120)

POS_SUP = [(150 + 30 * x, 120) for x in xrange(4)]
# POS_SUP_CHK	=	(120,120)

POS_DOCK = [(250, 165 + dock * 80) for dock in xrange(4)]
POS_REPAIR = (125, 365)
POS_REPAIR_YES = (500, 400)

POS_CHANGE_SORT = (780, 110)
POS_CHANGE_SHIP = [(410 + 340 * x, 217 + 113 * y)
                   for y in xrange(3) for x in xrange(2)]

POS_FORMATION = {"LINE_AHEAD": (446, 185), "LINE_ABREAST": (645, 345)}


with open("config.json") as f:
    config = json.loads(f.read())

exps = config["expedition"]
sortie = config["sortie"]


class ScreenShoter:

    """docstring for ScreenShoter"""

    def __init__(self, region=None):
        self.region = region

    def shot(self, region=None):
        if region == None:
            region = self.region
        return screenshot(region)


def match(screen, filename, path='img', threshold=300000, return_pos=False):
    template = cv2.imread(os.path.join(path, filename))
    res = cv2.matchTemplate(screen, template, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print min_loc, min_val, filename
    if return_pos:
        return min_val < threshold, min_loc
    else:
        return min_val < threshold


def terminate_thread(tid):
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """

    exc = ctypes.py_object(KeyboardInterrupt)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(tid), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        """if it returns a number greater than one, you're in trouble,
        and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def click_page(page):
    sleep(2)
    mouse.click(436, 457)
    sleep(1.5)
    if page < 5:
        mouse.click(516 + 31 * page, 450)
    else:
        mouse.click(516 + 31 * 4, 450)
        sleep(1)
        page -= 4
        while page > 2:
            mouse.click(516 + 31 * 4, 450)
            page -= 2
            sleep(1)
        mouse.click(516 + 31 * (page + 2), 450)
    sleep(1.5)


class AutoClick:

    """docstring for AutoClick"""

    def __init__(self):
        self.server = Server()
        thread.start_new_thread(self.server.start, ())
        self.orange = False
        self.flag = False
        self.argv = False
        self.mission = argv
        self.min_expdition_time = 0
        # self.t=threading.Thread(target=self.main)
        # self.t.setDaemon(True)
        # self.t.start()
        # self.tid=self.t.ident
        self.handle, self.tid = win32process.beginthreadex(
            None, 0, self.main, (), 0)
        # print type(self.t.ident)

    def init(self):
        tmp, pos = match(
            screenshot(), "setting.bmp", threshold=500000, return_pos=True)
        while not tmp:
            sleep(3)
            tmp, pos = match(
                screenshot(), "setting.bmp", threshold=500000, return_pos=True)

        self.stype = dict((key, [ship['api_sortno'] for ship in group]) for key, group in groupby(sorted(self.server.data[
                          '/kcsapi/api_start2']['api_data']['api_mst_ship'], key=itemgetter('api_stype')), key=itemgetter('api_stype')))

        self.ships_by_sortno = dict((ship['api_sortno'], ship) for ship in self.server.data[
                                    '/kcsapi/api_start2']['api_data']['api_mst_ship'])
        return pos[1] - 440, pos[1] + 40, pos[0] - 764, pos[0] + 36

    def launch(self):
        mouse.click(*POS_ATTACK)
        sleep(1)
        mouse.click(*POS_ATTACK)
        sleep(1)
        while not match(self.screen.shot(), "1_5.bmp"):
            sleep(1)
        self.sortie(*[int(x) for x in self.mission.split('-')])
        mouse.click(*POS_GO)
        sleep(1)
        screen = self.screen.shot()
        if match(screen, "orange.bmp") or match(screen, "red.bmp"):
            print "tired!"
            sleep(300)
            self.go_main()
            orange = True
            return False
        elif match(screen, "repair.bmp") or self.orange:
            print "tired!"
            sleep(300)
            self.go_main()
            orange = False
            return False
        mouse.click(*POS_GO)

        self.battle()

        return True

    def battle(self):
        advance = sortie[self.mission]["advance"]
        night = sortie[self.mission]["night"]
        if self.mission == '1-5':
            night = False
        else:
            night = True
        flag = 0
        sleep(5)
        while 1:
            while self.flag:
                sleep(1)
            formation = True
            check_night = True
            while flag == 0 and not self.flag:
                screen = self.screen.shot()
                if formation and check_night and match(screen, "compass.bmp"):
                    mouse.click(*POS_GO)
                elif formation and check_night and match(screen, "get.bmp"):
                    mouse.click(*POS_GO)
                    return
                elif formation and check_night and match(screen, "formation.bmp"):
                    mouse.click(
                        *POS_FORMATION[sortie[self.mission]["formation"]])
                    formation = False
                    sleep(20)
                elif self.server.path == "/kcsapi/api_req_sortie/battleresult":
                    sleep(3)
                    while not match(self.screen.shot(), "next_0.bmp"):
                        sleep(0.5)
                    mouse.click(*POS_GO)
                    flag = 1
                    sleep(3)
                elif check_night and match(screen, "night.bmp"):
                    if night:
                        mouse.click(*POS_BACK)
                    else:
                        mouse.click(*POS_NIGHT)
                    check_night = False
                    sleep(3)
                sleep(1)
            while flag == 1 and not self.flag:
                screen = self.screen.shot()
                if match(screen, "broken.bmp"):
                    advance = False
                    if match(self.screen.shot(region=get_region([self.box[2], self.box[0], 400, 235])), "broken.bmp"):
                        self.go_main()
                        return
                    # 327,202
                if match(screen, "next_1.bmp", threshold=500000):
                    mouse.click(*POS_GO)
                    flag = 2
                sleep(1)
            while flag == 2 and not self.flag:
                screen = self.screen.shot()
                if match(screen, "advance.bmp"):
                    if advance:
                        mouse.click(*POS_NIGHT)
                        flag = 0
                        sleep(5)
                        continue
                    else:
                        mouse.click(*POS_BACK)
                        return
                elif match(screen, "get.bmp"):
                    mouse.click(*POS_GO)
                elif self.server.path == '/kcsapi/api_port/port':
                    return
                sleep(1)
            sleep(1)

    def expedition_come_back(self):
        sleep(1)
        mouse.click(*POS_ATTACK)
        sleep(5)
        while not match(self.screen.shot(), "next_1.bmp"):
            sleep(1)
        mouse.click(*POS_GO)
        sleep(1)
        mouse.click(*POS_GO)

        self.need_supply = True

    def supply(self):
        mouse.click(*POS_SUPPLY)
        sleep(1)
        screen = self.screen.shot()
        while (screen[POS_SUPPLY1] == GRAY).all():
            mouse.click(*POS_SUPPLY1)
            sleep(2)
            mouse.click(*POS_SUPPLY2)
            sleep(3)
            screen = self.screen.shot()
        # if argv!='exp' and match(screen,"broken.bmp"):
        # 	mail.sendmail(['lanhao34@gmail.com'],"大破警告","大破警告")
        # 	argv='exp'
        for i in self.need_supply:
            mouse.click(*POS_SUP[i])
            sleep(1)
            while (self.screen.shot()[POS_SUPPLY1] == GRAY).all():
                mouse.click(*POS_SUPPLY1)
                sleep(1)
                mouse.click(*POS_SUPPLY2)
                sleep(3)

        self.go_main()

    def send_exps(self):
        def send_exp(team, stage, mission):
            if stage == 0 or mission == 0:
                return
            while not match(self.screen.shot(), 'decision.bmp'):
                mouse.click(*POS_EXP_STAGE[stage - 1])
                sleep(1)
                mouse.click(*POS_EXP_MISSION[mission - 1])
                sleep(1)
            mouse.click(*POS_GO)
            sleep(1)
            mouse.click(*POS_EXP_TEAM[team])
            sleep(1)
            click_time = time.time()
            mouse.click(*POS_GO)
            sleep(1)
            while self.server.time < click_time and self.server.path != '/kcsapi/api_get_member/deck':
                sleep(1)
            sleep(5)
        mouse.click(*POS_ATTACK)
        sleep(1)
        mouse.click(*POS_GO_EXP)
        sleep(3)
        for exp in set(self.need_exp):
            send_exp(exp, *exps[exp])
        self.need_exp.clear()
        sleep(3)
        self.go_main()

    def sortie(self, stage, mission):
        mouse.click(80 + 75 * stage, 440)
        sleep(1)
        if mission == 5:
            mouse.click(*POS_1_5)
            sleep(1)
            mouse.click(*POS_1_5)
        else:
            mouse.click(*POS_SORTIE[mission - 1])
        sleep(1)

    def repair(self):
        click_time = time.time()
        mouse.click(*POS_REPAIR)
        while self.server.path != '/kcsapi/api_get_member/ndock' or self.server.time < click_time:
            sleep(1)
        for ship_index, dock in self.need_repair:
            sleep(1)
            page = ship_index / 10
            row = ship_index % 10
            mouse.click(*POS_DOCK[dock])
            sleep(1)
            while not match(self.screen.shot(), "new.bmp"):
                mouse.click(*POS_CHANGE_SORT)
                sleep(0.2)
            click_page(page)
            mouse.click(600, 138 + row * 31)
            sleep(1)
            mouse.click(*POS_GO)
            sleep(1)
            click_time = time.time()
            mouse.click(*POS_REPAIR_YES)
            while self.server.path != '/kcsapi/api_get_member/ndock' or self.server.time < click_time:
                sleep(1)
        self.go_main()

    def change_ship(self):
        mouse.click(200, 135)
        for i, ship_index in self.need_replace:
            sleep(1.5)
            page = ship_index / 10
            row = ship_index % 10
            mouse.click(*POS_CHANGE_SHIP[i])
            sleep(1.5)
            while not match(self.screen.shot(), "new.bmp"):
                mouse.click(*POS_CHANGE_SORT)
                sleep(0.2)
            click_page(page)
            mouse.click(450, 168 + 28 * row)
            sleep(1)
            click_time = time.time()
            mouse.click(*POS_GO)
            sleep(1)
            while self.server.path != '/kcsapi/api_req_hensei/change' or self.server.time < click_time:
                sleep(1)
        self.go_main()

    def go_main(self):
        click_time = time.time()
        while self.server.path != '/kcsapi/api_port/port' or self.server.time < click_time:
            mouse.click(*POS_MAIN)
            sleep(1)

    def onKeyboardEvent(self, event):
        if event.Key == 'F9':
            if self.argv:
                self.argv = False
            else:
                self.argv = True
        if event.Key == 'F10':
            if self.flag:
                print "Press F10 to pause."
                win32process.ResumeThread(self.handle)
                self.flag = False
            else:
                print "Press F10 to continue."
                win32process.SuspendThread(self.handle)
                self.flag = True
        if event.Key == 'F8':
            # terminate_thread(self.tid)
            # sleep(0.5)
            win32api.PostThreadMessage(
                win32api.GetCurrentThreadId(), win32con.WM_QUIT, 0, 0)
        if event.Key == 'F12':
            # win32api.CloseHandle(self.handle)
            terminate_thread(int(self.tid))
            # win32api.PostThreadMessage(self.tid, win32con.WM_QUIT, 0, 0);
            print 'killed thread'
            self.handle, self.tid = win32process.beginthreadex(
                None, 0, self.main, (), 0)
            # self.t=threading.Thread(target=self.main)
            # self.t.setDaemon(True)
            # self.t.start()
            # self.tid=self.t.ident
        return True

    def run(self):
        hm = pyHook.HookManager()
        hm.KeyDown = self.onKeyboardEvent
        hm.HookKeyboard()
        self.thread_id = win32api.GetCurrentThreadId()
        pythoncom.PumpMessages()
        exit()

    def check_stype(self):
        if self.mission == 'exp':
            return
        elif self.mission in ('3-2', '2-3'):
            for i, id_list in enumerate(sortie[self.mission]["id_lists"]):
                if self.ship_team1[i] < 0 or self.ship_team1[i]not in id_list:
                    self.change_all()
                    return

    def change_all(self):
        self.need_replace = []
        if self.mission == 'exp':
            return
        elif self.mission in ('3-2', '2-3'):
            for i, id_list in enumerate(sortie[self.mission]["id_lists"]):
                tmp_index = -1
                tmp_cond = 0
                for ship_id in id_list:
                    ship = self.ships_by_id[ship_id]
                    if ship_id not in set(self.ship_team1) and ship['index'] not in set(x[1] for x in self.need_replace):
                        if tmp_cond < ship['api_cond']:
                            tmp_cond = ship['api_cond']
                            tmp_index = ship['index']
                if tmp_index!=-1:
                    self.need_replace.append([i, tmp_index])
        if self.ships[self.need_replace[0][1]]['api_id'] == self.ship_team1[0]:
            self.need_replace = self.need_replace[1:]
        mouse.click(200, 135)
        sleep(1)
        click_time = time.time()
        mouse.click(415, 120)
        if self.ship_team1[1] != -1:
            while self.server.path != '/kcsapi/api_req_hensei/change' or self.server.time < click_time:
                sleep(1)
        for i, ship_index in self.need_replace:
            sleep(2)
            page = ship_index / 10
            row = ship_index % 10
            mouse.click(*POS_CHANGE_SHIP[i])
            sleep(1)
            while not match(self.screen.shot(), "new.bmp"):
                mouse.click(*POS_CHANGE_SORT)
                sleep(0.2)
            click_page(page)
            sleep(1)
            mouse.click(450, 168 + 28 * row)
            sleep(1)
            click_time = time.time()
            mouse.click(*POS_GO)
            sleep(1)
            while self.server.path != '/kcsapi/api_req_hensei/change' or self.server.time < click_time:
                sleep(1)
        self.go_main()

    def update_data(self):
        now_time = time.time()
        self.min_expdition_time = now_time + 9999
        self.max_repair_time = 0
        need_repair = set()
        need_replace = set()
        self.need_supply = set()

        port_api_data = self.server.data['/kcsapi/api_port/port']['api_data']
        self.ship_team1 = port_api_data['api_deck_port'][0]['api_ship']
        self.ships = port_api_data['api_ship']
        self.ships.reverse()
        self.ships_by_id = {ship['api_id']: dict(ship, index=i) for i, ship in enumerate(self.ships)}
        empty_dock = [i for i, dock in enumerate(
            port_api_data['api_ndock']) if dock['api_state'] == 0]
        ship_in_dock = set(dock['api_ship_id']
                           for dock in port_api_data['api_ndock'])

        for i, deck in enumerate(port_api_data['api_deck_port']):
            t = deck['api_mission'][2] / 1000
            if 0 < t < self.min_expdition_time:
                self.min_expdition_time = t
            elif t == 0:
                if i != 0 and exps[i - 1][0] != 0:
                    self.min_expdition_time = 0
                    self.need_exp.add(i - 1)
                for api_id in deck['api_ship']:
                    if api_id < 0:
                        break
                    ship = self.ships_by_id[api_id]
                    ship_data = self.ships_by_sortno[ship['api_sortno']]
                    if ship_data['api_fuel_max'] > ship['api_fuel'] or ship_data['api_bull_max'] > ship['api_bull']:
                        self.need_supply.add(i)
                        break

        for i, ship_id in enumerate(self.ship_team1):
            if ship_id == -1:
                break
            ship = self.ships_by_id[ship_id]

            if ship_id in ship_in_dock:
                need_replace.add(i)
            elif ship['api_cond'] < 33:
                need_replace.add(i)
                self.max_repair_time = max(
                    self.max_repair_time, now_time + (33 - ship['api_cond']) / 3 * 180 + 180)
                if ship['api_ndock_time'] > 0:
                    need_repair.add(ship['index'])
            elif ship['api_maxhp'] >= ship['api_nowhp'] * 2:
                need_repair.add(ship['index'])
                need_replace.add(i)

        for dock in port_api_data['api_ndock']:
            if dock['api_ship_id'] in self.ship_team1:
                self.max_repair_time = max(
                    self.max_repair_time, dock['api_complete_time'] / 1000)

        self.need_replace = []
        if self.mission in ('3-2', '2-3'):
            for i in need_replace:
                tmp_index = None
                tmp_cond = 0
                id_list = sortie[self.mission]["id_lists"][i]
                for ship_id in id_list:
                    ship = self.ships_by_id[ship_id]
                    if ship_id not in set(self.ship_team1) | ship_in_dock and ship['index'] not in set(x[1] for x in self.need_replace):
                        if tmp_cond < ship['api_cond'] and (ship['api_cond'] > self.ships_by_id[self.ship_team1[i]]['api_cond'] or self.ship_team1[i] in ship_in_dock):
                            tmp_cond = ship['api_cond']
                            tmp_index = ship['index']
                if tmp_index:
                    self.need_replace.append([i, tmp_index])

        wait_time = self.max_repair_time - now_time
        if wait_time > 0 and not self.need_replace:
            for ship_id in set(self.ship_team1) - {-1} - ship_in_dock:
                if 0 < self.ships_by_id[ship_id]['api_ndock_time'] / 1000 < wait_time:
                    need_repair.add(self.ships_by_id[ship_id]['index'])

        self.need_repair = zip(need_repair, empty_dock)

        self.max_repair_time -= 120
        self.min_expdition_time -= 120
        self.max_repair_time = min(
            self.max_repair_time, self.min_expdition_time)
        print 'exp=%s\nrepair=%s\nreplace=%s' % (self.need_exp, self.need_repair, self.need_replace)

        # data={ship['api_sortno']:ship for ship in self.server.data['/kcsapi/api_start2']['api_data']['api_mst_ship']}
        # with open('ships_sortno.txt','w') as f:
        # 	for ship in self.ships:
        # 		f.write("%s\t%s\t%s\n"%(ship['api_sortno'], data[ship['api_sortno']]['api_name'].encode('utf-8'), ship['api_lv']))

    def main(self):
        # print
        # self.server.data['/kcsapi/api_port/port']['api_data']['api_deck_port'][0]['api_ship']

        # self.tid=win32api.GetCurrentThreadId()
        # sleep(1)
        # print self.tid
        self.box = self.init()
        self.screen = ScreenShoter(
            region=get_region([self.box[2], self.box[0], 800, 480]))
        mouse.setoffset(self.box[2], self.box[0])
        self.need_supply = set()
        self.need_exp = set()
        self.need_repair = []
        self.need_replace = []
        need_check_stype = True

        screen = self.screen.shot()
        if match(screen, "setting.bmp"):
            self.supply()
        elif match(screen, "expedition.bmp"):
            self.expedition_come_back()
        # else:
        # 	self.go_main()

        while 1:
            while self.flag:
                sleep(1)
            screen = self.screen.shot()
            if match(screen, "expedition.bmp"):
                self.expedition_come_back()
                # self.go_main()
            elif match(screen, "launch.bmp"):
                self.update_data()
                if self.need_supply:
                    self.supply()
                elif self.need_exp:
                    self.send_exps()
                elif self.need_repair:
                    self.repair()
                elif self.need_replace:
                    self.change_ship()
                elif self.argv or not self.mission:
                    self.mission = raw_input("Input argument:")
                    self.check_stype()
                    self.argv = False
                elif self.mission == 'exp':
                    if self.min_expdition_time > time.time() - 60:
                        print time.strftime("next click: %H:%M:%S", time.localtime(self.min_expdition_time + 60))
                        while self.min_expdition_time > time.time():
                            sleep(60)
                        sleep(60 + self.min_expdition_time - time.time())
                    if match(self.screen.shot(), "setting.bmp"):
                        self.supply()
                    else:
                        sleep(3)
                        self.go_main()
                elif need_check_stype:
                    self.check_stype()
                    need_check_stype = False
                elif self.mission:
                    if self.max_repair_time > time.time() - 60:
                        print time.strftime("next click: %H:%M:%S", time.localtime(self.max_repair_time + 60))
                        while self.max_repair_time > time.time():
                            sleep(60)
                        sleep(60 + self.max_repair_time - time.time())
                        if match(self.screen.shot(), "setting.bmp"):
                            self.supply()
                        else:
                            sleep(3)
                            self.go_main()
                    else:
                        self.launch()
            sleep(1)

if __name__ == '__main__':
    ac = AutoClick()
    mouse.ac = ac
    ac.run()
