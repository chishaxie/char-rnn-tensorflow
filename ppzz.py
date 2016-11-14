#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import logging

import jieba
jieba.setLogLevel(logging.CRITICAL)

import pinyin
import pypinyin
import Levenshtein

def pz(char):
    r = pinyin.get(char, format="numerical", delimiter=" ")
    assert " " not in r
    sd = r[-1]
    if sd == '1' or sd == '2' or sd == '5': # 5是轻声?
        return 'p'
    elif sd == '3' or sd == '4':
        return 'z'
    else:
        print char
        assert 0

fmt_7j = re.compile(ur'^(.{7})，(.{7})。(.{7})，(.{7})。$')
std_pz_7j = [
    (u'(平)平(仄)仄仄平平,(仄)仄平平仄仄平,(仄)仄(平)平平仄仄,(平)平(仄)仄仄平平', '124'),
    (u'(平)平(仄)仄平平仄,(仄)仄平平仄仄平,(仄)仄(平)平平仄仄,(平)平(仄)仄仄平平', '24'),
    (u'(仄)仄(平)平仄仄平,(平)平(仄)仄仄平平,(平)平(仄)仄平平仄,(仄)仄平平仄仄平', '124'),
    (u'(仄)仄(平)平平仄仄,(平)平(仄)仄仄平平,(平)平(仄)仄平平仄,(仄)仄平平仄仄平', '24'),
]
# 十八韵：
std_yy = {
    'a': 1, 'ua': 1, 'ia': 1, # 一麻，新华字典里的韵母 a、ua、ia 同属一个韵部。
    'o': 2, 'uo':2, # 二波，韵母 o、uo。
    'e': 3, # 三歌，韵母 e。
    'ie': 4, 'ue': 4, # 四皆，韵母 ie、ue。
    'i': 5, # 五支，韵母 i (属 zh、ch、sh、z、c、s声母，与七齐有别)。
    'er': 6, # 六儿，韵母 er。
    #'i': 7, # 七齐，韵母 i (属声母 b、p、m、f、d、t、n、l、j、q、x、y，有别于五支)。
    'ei': 8, 'ui': 8, # 八微，韵母 ei、ui。
    'ai': 9, 'uai': 9, # 九开，韵母 ai、uai。
    'u': 10, # 十姑，韵母 u。
    'v': 11, # 十一鱼，韵母 v。
    'ou': 12, 'iu': 12, # 十二侯，韵母 ou、iu。
    'ao': 13, # 十三豪，韵母 ao。
    'an': 14, 'ian': 14, 'uan': 14, # 十四寒，韵母 an、ian、uan。
    'en': 15, 'in': 15, 'un': 15, 'vn': 15, # 十五痕，韵母 en、in、un、vn。
    'ang': 16, 'uang': 16, 'iang': 16, # 十六唐，韵母 ang、uang、iang。
    'eng': 17, 'ing': 17, # 十七庚，韵母 eng、ing。
    'ong': 18, 'iong': 18, # 十八东，韵母 ong、iong。
}

def _pre():
    global std_pz_7j
    for i, ss in enumerate(std_pz_7j):
        s = ss[0]
        s = s.replace(u'(平)', '*').replace(u'(仄)', '*')
        s = s.replace(u'平', 'p').replace(u'仄', 'z').replace(',', '')
        std_pz_7j[i] = (str(s), ss[1])
    def expand_star(srcs):
        r = []
        for ss in srcs:
            s = ss[0]
            i = s.index('*')
            r.append((s[:i] + 'p' + s[i+1:], ss[1]))
            r.append((s[:i] + 'z' + s[i+1:], ss[1]))
        return r
    for i in range(7):
        std_pz_7j = expand_star(std_pz_7j)
_pre()

def pz_for_7j(s):
    m = fmt_7j.search(s)
    assert m
    s = ''.join([m.group(1), m.group(2), m.group(3), m.group(4)])
    r = ''.join([pz(c) for c in s])
    #print r
    max_d = 28
    max_i = -1
    for i, ts in enumerate(std_pz_7j):
        t = ts[0]
        d = Levenshtein.hamming(r, t)
        if d < max_d:
            max_d = d
            max_i = i
    yy = std_pz_7j[max_i][1]
    if yy == '124':
        ss = s[6] + s[13] + s[27]
    elif yy == '24':
        ss = s[13] + s[27]
    else:
        assert 0
    yms = [pypinyin.lazy_pinyin(c, style=pypinyin.STYLE_FINALS)[0] for c in ss]
    yyg = [std_yy[ym] if ym in std_yy else 99 for ym in yms]
    #print yy, ss, yms, yyg
    return max_d, len(set(yyg)) - 1

if __name__ == '__main__':
    #print len(std_pz_7j)
    print pz_for_7j(u'朝辞白帝彩云间，千里江陵一日还。两岸猿声啼不尽，轻舟已过万重山。')
    print pz_for_7j(u'山外青山楼外楼，西湖歌舞几时休。暖风熏得游人醉，直把杭州当汴州。')
    print pz_for_7j(u'春宵一刻值千金，花有清香月有阴。歌管楼亭声细细，秋千院落夜沉沉。')
