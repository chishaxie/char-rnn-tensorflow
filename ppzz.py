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
std_yy = {
    'a': 1, 'ia': 1, 'ua': 1,
    'ai': 2, 'uai': 2,
    'an': 3, 'ian': 3, 'uan': 3, 'van': 3,
    'ang': 4, 'iang': 4, 'uang': 4,
    'ao': 5, 'iao': 5,
    'e': 6, 'o': 6, 'uo': 6,
    'ei': 7, 'ui': 7,
    'en': 8, 'in': 8, 'un': 8, 'vn': 8,
    'eng': 9, 'ing': 9, 'ong': 9, 'iong': 9,
    'i': 10, 'er': 10,
    'ie': 11, 'ye': 11,
    'ou': 12, 'iu': 12,
    'u': 13,
    'v': 14,
    've': 15,
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
    yyg = [std_yy[ym] if ym in std_yy else 16 for ym in yms]
    #print yy, ss, yms, yyg
    return max_d, len(set(yyg)) - 1

if __name__ == '__main__':
    #print len(std_pz_7j)
    print pz_for_7j(u'朝辞白帝彩云间，千里江陵一日还。两岸猿声啼不尽，轻舟已过万重山。')
    print pz_for_7j(u'山外青山楼外楼，西湖歌舞几时休。暖风熏得游人醉，直把杭州当汴州。')
    print pz_for_7j(u'春宵一刻值千金，花有清香月有阴。歌管楼亭声细细，秋千院落夜沉沉。')
