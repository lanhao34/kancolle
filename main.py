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

RED = [32, 32, 255]
GREEN = [32, 200, 64]
GRAY = [68, 68, 68]

POS_ATTACK = (196, 266)
POS_1_5 = (705, 250)
POS_GO = (660, 445)
POS_SUPPLY = (77, 222)
POS_SUPPLY1 = (117, 117)
POS_SUPPLY2 = (700, 440)
POS_MAIN = (50, 50)
POS_LEFT = (290, 240)
POS_RIGHT = (510, 242)

POS_PAGE_2 = (235, 440)
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
POS_EXP_PAGE_3 = (260, 440)  # _3
# POS_EXP_21	=	(200,235) #3

POS_EXP_MISSION = [(200, 170 + i * 30) for i in xrange(8)]
POS_EXP_PAGE = [(140 + 60 * i, 440)for i in xrange(5)]

# POS_EXP_21	=	(200,200) #2

POS_GO_EXP = (680, 220)

POS_SUP = [(150 + 30 * x, 120) for x in xrange(4)]
POS_CHANGE_TEAM = [(135 + 30 * x, 120) for x in xrange(4)]
# POS_SUP_CHK	=	(120,120)

POS_DOCK = [(250, 165 + dock * 80) for dock in xrange(4)]
POS_REPAIR = (125, 365)
POS_REPAIR_YES = (500, 400)
POS_FAST_REPAIR = (735,290)

POS_CHANGE_SORT = (780, 110)
POS_CHANGE_SHIP = [(410 + 340 * x, 217 + 113 * y)
                   for y in xrange(3) for x in xrange(2)]

POS_FORMATION = {"LINE_AHEAD": (446, 185), "LINE_ABREAST": (645, 345)}

flat = lambda L: sum(map(flat,L),[]) if isinstance(L,list) else [L]

with open("config.json") as f:
    config = json.loads(f.read())

exps = [(x[0],x[1]) for x in config["expedition"]]
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
        # raise ValueError("nonexistent thread id")
        print "nonexistent thread id"
    elif res > 1:
        """if it returns a number greater than one, you're in trouble,
        and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        # raise SystemError("PyThreadState_SetAsyncExc failed")
        print "PyThreadState_SetAsyncExc failed"


class AutoClick:

    """docstring for AutoClick"""

    def __init__(self):
        self.server = Server()
        thread.start_new_thread(self.server.start, ())
        self.suspended = False
        self.new_argv = ''
        if len(sys.argv) > 1:
            self.mission = sys.argv[1]
        else:
            self.mission = 'exp'
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
        if match(screen, "orange.bmp") or match(screen, "red.bmp") or match(screen, "repair.bmp") or match(screen, "broken.bmp"):
            print "tired!"
            sleep(300)
            self.go_main()
            return False

        mouse.click(*POS_GO)

        self.battle()

        return True

    def battle(self):
        if self.mission in sortie.keys():
            advance = sortie[self.mission]["advance"]
            night = sortie[self.mission]["night"]
        else:
            temp = raw_input("Do you want to advance?(Y/N)")
            if temp.upper() == 'Y':
                advance = True
            else:
                advance = False
            temp = raw_input("Do you want to fight at midnight?(Y/N)")
            if temp.upper() == 'Y':
                night = True
            else:
                night = False
        flag = 0
        sleep(5)
        while 1:
            formation = True
            check_night = True
            while flag == 0:
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
                    self.server.path = ''
                    sleep(3)
                    while not match(self.screen.shot(), "next_0.bmp"):
                        sleep(0.5)
                    mouse.click(*POS_GO)
                    flag = 1
                    sleep(3)
                elif check_night and match(screen, "night.bmp"):
                    if night:
                        mouse.click(*POS_RIGHT)
                    else:
                        mouse.click(*POS_LEFT)
                    check_night = False
                    sleep(3)
                sleep(1)
            while flag == 1:
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
            while flag == 2:
                screen = self.screen.shot()
                if match(screen, "advance.bmp"):
                    if advance:
                        mouse.click(*POS_LEFT)
                        flag = 0
                        sleep(5)
                        continue
                    else:
                        mouse.click(*POS_RIGHT)
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
        def send_exp(team, PAGE, mission):
            if PAGE == 0 or mission == 0:
                return
            while not match(self.screen.shot(), 'decision.bmp'):
                mouse.click(*POS_EXP_PAGE[PAGE - 1])
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

    def sortie(self, PAGE, mission):
        mouse.click(80 + 75 * PAGE, 440)
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
            self.click_page(page)
            mouse.click(600, 138 + row * 31)
            sleep(1)
            if self.mission not in {'3-2','2-3','exp'}:
                mouse.click(*POS_FAST_REPAIR)
                sleep(1)
            mouse.click(*POS_GO)
            sleep(1)
            click_time = time.time()
            mouse.click(*POS_REPAIR_YES)
            while self.server.path not in  {'/kcsapi/api_get_member/ndock','/kcsapi/api_req_nyukyo/start'} or self.server.time < click_time:
                sleep(1)
        self.go_main()

    def change_ship(self):
        mouse.click(200, 135)
        sleep(1.5)
        mouse.click(*POS_CHANGE_TEAM[self.change_ship_team])
        sleep(1.5)
        if self.need_clear:
            sleep(1)
            click_time = time.time()
            mouse.click(415, 120)
            if self.ship_team[self.change_ship_team][1] != -1:
                while self.server.path != '/kcsapi/api_req_hensei/change' or self.server.time < click_time:
                    sleep(1)
        sleep(1)
        for i, ship_index in self.need_replace:
            sleep(1)
            page = ship_index / 10
            row = ship_index % 10
            mouse.click(*POS_CHANGE_SHIP[i])
            sleep(1)
            while not match(self.screen.shot(), "new.bmp"):
                mouse.click(*POS_CHANGE_SORT)
                sleep(0.2)
            self.click_page(page)
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
            thread.start_new_thread(self.change_argv, ())
        if event.Key == 'F10':
            if self.suspended:
                print "Press F10 to pause."
                win32process.ResumeThread(self.handle)
                self.suspended = False
            else:
                print "Press F10 to continue."
                win32process.SuspendThread(self.handle)
                self.suspended = True
        if event.Key == 'F8':
            win32api.PostThreadMessage(
                win32api.GetCurrentThreadId(), win32con.WM_QUIT, 0, 0)
        if event.Key == 'F12':
            print 'killed thread'
            self.suspended = False
            terminate_thread(int(self.tid))
            self.handle, self.tid = win32process.beginthreadex(
                None, 0, self.main, (), 0)
        return True

    def change_argv(self):
        win32process.SuspendThread(self.handle)
        self.new_argv = raw_input("\r\nInput argument:")
        win32process.ResumeThread(self.handle)

    def run(self):
        hm = pyHook.HookManager()
        hm.KeyDown = self.onKeyboardEvent
        hm.HookKeyboard()
        self.thread_id = win32api.GetCurrentThreadId()
        pythoncom.PumpMessages()
        exit()

    def check_stype(self, team = 0):
        print "Check ship type of team %s"%team

        if self.mission == '1-1' and self.need_flash!=0:
            id_lists=[flat(config['exp_id_lists']['%s,%s'%exps[self.need_flash-1]]["id_lists"])]
        elif team!=0 and '%s,%s'%exps[team-1] in config['exp_id_lists'].keys():
            id_lists=config['exp_id_lists']['%s,%s'%exps[team-1]]["id_lists"]
        elif self.mission in sortie.keys():
            id_lists=sortie[self.mission]["id_lists"]
        else:
            return False
        for i, id_list in enumerate(id_lists):
            if self.ship_team[team][i] == -1 or self.ship_team[team][i] not in id_list:
                print self.ship_team[team][i],id_list
                self.change_all_ship(team)
                return True
        if i!=5 and self.ship_team[team][i+1] != -1:
            self.change_all_ship(team)
            return True
        return False

    def change_all_ship(self, team = 0):
        self.need_replace = []
        self.need_clear = True
        if self.mission == '1-1' and self.need_flash!=0:
            self.need_replace = [[0,self.ships_by_id[config['exp_id_lists']['%s,%s'%exps[self.need_flash-1]]['id_lists'][0][0]]['index']]]
        elif team!=0:
            self.change_ship_team = team
            for i,ship_id in enumerate(flat(config['exp_id_lists']['%s,%s'%exps[team-1]]['id_lists'])):
                self.need_replace.append([i,self.ships_by_id[ship_id]['index']])
        else:
            for i, id_list in enumerate(sortie[self.mission]["id_lists"]):
                tmp_index = -1
                tmp_cond = 0
                for ship_id in id_list:
                    ship = self.ships_by_id[ship_id]
                    if ship_id not in set(self.ship_team[0]) and ship['index'] not in set(x[1] for x in self.need_replace):
                        if tmp_cond < ship['api_cond']:
                            tmp_cond = ship['api_cond']
                            tmp_index = ship['index']
                if tmp_index != -1:
                    self.need_replace.append([i, tmp_index])
       
        if self.ships[self.need_replace[0][1]]['api_id'] == self.ship_team[self.change_ship_team][0]:
            self.need_replace = self.need_replace[1:]
        self.change_ship()
            
    def click_page(self, page):
        sleep(1)
        mouse.click(436, 457)
        sleep(1)
        if page < 5:
            mouse.click(516 + 31 * page, 450)
        elif page == (len(self.ships) - 1) / 10:
            mouse.click(715, 457)
        else:
            mouse.click(516 + 31 * 4, 450)
            sleep(1)
            page -= 4
            while page > 2:
                mouse.click(516 + 31 * 4, 450)
                page -= 2
                sleep(1)
            mouse.click(516 + 31 * (page + 2), 450)
        sleep(1)

    def update_data(self):
        now_time = time.time()
        self.min_expdition_time = now_time + 9999
        self.max_repair_time = 0
        self.change_ship_team = 0
        self.need_clear = False
        need_repair = set()
        need_replace = set()
        self.need_supply = set()

        port_api_data = self.server.data['/kcsapi/api_port/port']['api_data']
        self.ship_team = [x['api_ship'] for x in port_api_data['api_deck_port']]
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

        for i in list(self.need_exp):
            if '%s,%s'%exps[i] in config['exp_id_lists'].keys():
                for id_list in config['exp_id_lists']['%s,%s'%exps[i]]['id_lists']:
                    for ship_id in id_list:
                        if self.mission!='1-1' and self.ships_by_id[ship_id]['api_cond']<53:
                            self.mission='1-1'
                            self.need_exp-={i}
                            self.need_flash=i+1
                            print "Change into flash mode! Team %s"%self.need_flash
                            if self.check_stype():
                                return True
                        elif self.mission=='1-1' and self.ships_by_id[ship_id]['api_cond']<75:
                            self.need_exp-={i}
                            break
                if i in self.need_exp:
                    if self.mission=='1-1':
                        for id_list in config['exp_id_lists']['%s,%s'%exps[i]]['id_lists']:
                            if self.ship_team[0][0] in id_list:
                                self.need_replace=[[0,self.ships_by_id[config['akashi']]['index']]]
                                return False
                        self.mission = 'exp'
                        print "Change into expedition mode!"
                    if self.check_stype(i+1):
                        return True


        for i, ship_id in enumerate(self.ship_team[0]):
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
            if dock['api_ship_id'] in self.ship_team[0]:
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
                    if ship_id not in self.ship_team[0] and ship['index'] not in set(x[1] for x in self.need_replace):
                        if ship['api_maxhp'] >= ship['api_nowhp'] * 2 or (ship['api_cond'] < 33 and ship['api_ndock_time'] > 0):
                            if ship_id not in ship_in_dock:
                                need_repair.add(ship['index'])
                        elif tmp_cond < ship['api_cond'] and (ship['api_cond'] > self.ships_by_id[self.ship_team[0][i]]['api_cond'] or self.ship_team[0][i] in ship_in_dock):
                            tmp_cond = ship['api_cond']
                            tmp_index = ship['index']
                if tmp_index != None:
                    self.need_replace.append([i, tmp_index])
                else:
                    self.max_repair_time = time.time() + 300
                    for dock in port_api_data['api_ndock']:
                        if self.max_repair_time>dock['api_complete_time']>0:
                            self.max_repair_time=dock['api_complete_time']

        elif self.mission == '1-1':
            if self.ships_by_id[self.ship_team[0][0]]['api_cond']>75 or need_replace or self.ship_team[0][0] not in flat(config['exp_id_lists']['%s,%s'%exps[self.need_flash-1]]['id_lists']):
                for ship_id in flat(config['exp_id_lists']['%s,%s'%exps[self.need_flash-1]]['id_lists']):
                    if ship_id not in ship_in_dock and self.ships_by_id[ship_id]['api_cond']<=75:
                        self.need_replace=[[0,self.ships_by_id[ship_id]['index']]]
                        break
        wait_time = self.max_repair_time - now_time
        if wait_time > 0 and not self.need_replace:
            for ship_id in set(self.ship_team[0]) - {-1} - ship_in_dock:
                if 0 < self.ships_by_id[ship_id]['api_ndock_time'] / 1000 < wait_time:
                    need_repair.add(self.ships_by_id[ship_id]['index'])

        self.need_repair = zip(need_repair, empty_dock)

        if need_repair and not empty_dock and not self.need_replace:
            for dock in port_api_data['api_ndock']:
                self.max_repair_time = min(
                    self.max_repair_time, dock['api_complete_time'] / 1000)

        self.max_repair_time -= 120
        self.min_expdition_time -= 120
        self.max_repair_time = min(
            self.max_repair_time, self.min_expdition_time)
        print self.mission
        print 'exp=%s\nrepair=%s\nreplace=%s' % (self.need_exp, self.need_repair, self.need_replace)
        return False
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
        self.need_flash = -1
        self.need_repair = []
        self.need_replace = []
        self.need_check_stype = True

        screen = self.screen.shot()
        if match(screen, "setting.bmp"):
            self.supply()
        elif match(screen, "expedition.bmp"):
            self.expedition_come_back()
        # else:
        # 	self.go_main()

        while 1:
            while self.suspended:
                sleep(1)
            screen = self.screen.shot()
            if match(screen, "expedition.bmp"):
                self.expedition_come_back()
                # self.go_main()
            elif match(screen, "launch.bmp"):
                if self.update_data():
                    pass
                elif self.need_supply:
                    self.supply()
                elif self.need_repair:
                    self.repair()
                elif self.need_replace:
                    self.change_ship()
                elif self.need_check_stype:
                    self.check_stype()
                    self.need_check_stype = False
                elif self.need_exp:
                    self.send_exps()
                elif self.new_argv:
                    self.mission = self.new_argv
                    self.update_data()
                    self.check_stype()
                    self.new_argv = ''
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
                elif self.mission:
                    print self.mission
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
                else:
                    print self.mission
            sleep(1)

if __name__ == '__main__':
    ac = AutoClick()
    mouse.ac = ac
    ac.run()
