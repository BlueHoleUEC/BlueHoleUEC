# coding:utf-8
#python3でMeCabを動かし名詞抽出を行うモジュール
#(注意!)辞書(mecab-ipadic-neologd)を指定
#(条件)MeCabをpythonから利用することができる
#MeCabの最新辞書(mecab-ipadic-neologd)がインストールされていること。

#python のバージョン指定：python 3.5.0


import sys
import MeCab




def mecab_general_noun_get(text):
        #一般(固有)名詞の獲得
        #MeCab
        mThings = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
        mThings.parse('')
        node = mThings.parseToNode(text)
        #エラー回避のためにリストにnullを入れておく
        keywords = ['null']

        while node:
            if node.feature.split(',')[0] == '名詞':
                if node.feature.split(',')[1] not in ['代名詞','非自立','数','接尾'] :
                    keywords.insert(0,node.surface)
            node = node.next
        print('-----------------')
        #print('一般名詞を抽出しました、イベントカテゴリーにはどの名詞を採用しますか？(1~の番号を入力)')
        #print('当てはまる名詞がない場合は"null"を選択')
        #print(keywords)
        
        #num = int(input("input : "))
        #num = num - 1
        #return keywords[num]
        return keywords
'''
def mecab_where_get(text):
        #一般(固有)名詞の獲得
        #MeCab
        mThings = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
        mThings.parse('')
        node = mThings.parseToNode(text)
        #エラー回避のためにリストにnullを入れておく
        keywords = ['null']
        while node:
            if node.feature.split(',')[0] == '名詞':
                if node.feature.split(',')[1] != '代名詞' and node.feature.split(',')[1] != '非自立':
                    keywords.insert(0,node.surface)
            node = node.next
        print('-----------------')
        print("一般名詞を抽出しました、場所カテゴリーにはどの名詞を採用しますか？(1~の番号を入力)")
        print('当てはまる名詞がない場合は"null"を選択')
        print(keywords)
        
        #num = int(input("input : "))
        #num = num - 1
        #return keywords[num]
        return keywords
'''

def mecab_name_get(text):
        #人名を獲得
        ###MeCab
        mThings = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
        mThings.parse('')
        node = mThings.parseToNode(text)
        #エラー回避のためにリストにnullを入れておく
        keywords = ['null']
        while node:
            if node.feature.split(',')[2] == '人名':
                keywords.insert(0,node.surface)
            node = node.next
        return keywords
