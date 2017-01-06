# coding: utf-8
#!/usr/bin/env python

#python のバージョン指定：python 3.5.0
#(条件)MeCabをpythonから利用することができる



import json
import sys
import os
import codecs
import MeCab
import re
import datetime
#----外ファイルインポート----
import python_mecab
import get_nlc 
import get_day 
import record
import ans_main_t3
import add_q_main
from k3.main import K3

today = 25

#　入力
st = input('Input: ')
#st = "明日の西野先生の講演会はどこで行われますか？"

#履歴の表示
#"input:"に[履歴]が入力されたら、即履歴を表示して終了
#最後の「履歴」が追加でcsvファイルに書き込まれないように
#この位置指定!!
get_record = re.search('履歴', st)
if get_record :
	dataReader_user = record.record_user_read()
	for row in dataReader_user:
		print(row)
	dataReader_sys  = record.record_sys_read()
	for row in dataReader_sys:
		print(row)
	sys.exit()


#履歴(ユーザー)の作成
#引数'u'はユーザー入力を示す
record.record_make_user(st,'u')


#データを格納する辞書の作成
data ={'category' :'null',
	   'what'     :[],
	   'where'    :[],
	   'who'      :[],
	   'when_time':[],
	   'when_day' :[],
	   'how_time' :[]}


#　get_nlcからカテゴリータグの取得
category_ans = get_nlc.nlc_0(st)
category ='カテゴリー: '
print( category + category_ans)
data['category']=category_ans


#一般(固有)名詞の取得
if category_ans != 'what':
	#python_mecab.pyのmecab関数を利用
	mecab_noun = python_mecab.mecab_general_noun_get(st)
	data['what']=mecab_noun

'''
#場所名詞の取得
if category_ans != 'where':
	mecab_where = python_mecab.mecab_where_get(st)
	data['where']=mecab_where
'''


#人名の取得
mecab_name = python_mecab.mecab_name_get(st)
data['who']=mecab_name


#時間を表現する数字の取得(import reを使用)
t = re.search('\d+',st)
if t != None:
	time = t.group()
	data['when_time']=[time]

#ユーザー発話から日付情報を獲得してくる
data['when_day'] =  [get_day.get_day(st,today)]



#とりあえずの結果表示
#print (data)


#情報検索部でDBの検索
result = ans_main_t3.search(data)

ans_count = len(result)

ans_main_t3.anser(data,category_ans,ans_count,result)
