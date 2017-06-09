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
import get_day_time
import record
import add_q_main
import main_t3
import ans_main_t3
from k3.main import K3



def start():
	#日付の指定
	today = 25

	record.record_A('----- conversation start -----')

	#前回までの行数を把握しておく
	r_read = record.record_read()
	count_row_start = -1
	for row in r_read :
		count_row_start +=  1 




	print('>質問は何でしょうか？')
	#　入力
	st = input('Input: ')
	
	#履歴(ユーザー)の作成
	#引数'u'はユーザー入力を示す
	record.rfu(st)


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

	if data['category'] == 'why' or data['category'] == 'how':
		print('>category is why or how')
		record.rfs('>スタッフの方に引き継ぎます。')
		#終了
		record.record_A('----- conversation end   -----')
		#履歴の表示
		df = pandas.read_csv('conversation_log.csv')
		print_record = df[count_row_start:]
		print(print_record)
		sys.exit()

	#一般(固有)名詞の取得
	#python_mecab.pyのmecab関数を利用
	mecab_noun = python_mecab.mecab_general_noun_get(st)
	data['what']=mecab_noun

	'''
	#whatと統合してk3に投げる
	#場所名詞の取得
	if category_ans != 'where':
		mecab_where = python_mecab.mecab_where_get(st)
		data['where']=mecab_where
	'''

	#人名の取得
	mecab_name = python_mecab.mecab_name_get(st)
	data['who']=mecab_name

	#ユーザー発話から時間の獲得
	data['when_time'] = [get_day_time.get_time(st)]


	#ユーザー発話から日付情報を獲得してくる
	data['when_day'] =  [get_day_time.get_day(st,today)]
	print(data)

	#情報検索部でDBの検索
	results = ans_main_t3.look_k3(data)
	
	
	#システム応答の生成
	ans_main_t3.anser(data,category_ans,0,results,count_row_start)


main_t3.start()