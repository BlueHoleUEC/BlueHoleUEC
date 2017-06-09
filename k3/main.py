# coding:utf-8

"""
brew update
brew install mysql
unset TMPDIR
mysql_install_db --verbose --user=`whoami` --basedir="$(brew --prefix mysql)" --datadir=/usr/local/var/mysql
 # 起動時に MySQL を立ち上げる。
ln -sfv /usr/local/opt/mysql/*.plist ~/Library/LaunchAgents 
launchctl load -w ~/Library/LaunchAgents/homebrew.mxcl.mysql.plist

mysql.server start
(sudo mysql.server start)
mysql -u root 
(mysql -u root -p)

 # ここから、起動したMySQL上で入力
-- 新しくデータベースを作成する
CREATE DATABASE k3;
-- 新しくユーザーを作成する
CREATE USER 'k3'@'localhost' IDENTIFIED BY 'k3_password';
-- 作成したユーザーに作成したデータベースの操作権限を付与する
GRANT ALL PRIVILEGES ON k3.* TO 'k3'@'localhost';
-- 設定を反映する
FLUSH PRIVILEGES;
EXIT;
 # ここまで、起動したMySQL上で入力

pip install sqlalchemy
pip install PyMySQL

 # DBの内容を簡単に確認するには、MySQLWorkbenchをインストールしてください
 
K3をソースコードで使用する
from k3.main import K3

# k3の読み込み
k3 = K3()

# 検索要求の受け渡し
k3.set_params(data)

# 検索実行
result = k3.search()

"""

from pprint import pprint
from sqlalchemy import (
    create_engine,
    not_
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from operator import itemgetter, add
Base = declarative_base()

from k3.models.knowledge import Knowledge

class K3:
  
  MODE_STR = {
    'and': 0,
    'or': 1
  }

  def __init__(self, debug = False):
    self.debug = (debug == True)
    
    self.engine = create_engine('mysql+pymysql://k3:k3_password@localhost/k3?charset=utf8', echo=False)
    Session = sessionmaker(bind=self.engine)
    self.session = Session()
    
    self.mode = self.MODE_STR['and']
    self.category = 'what'

    self.params = {
      'what': [],
      'when_time': [],
      'when_day': [],
      'who': [],
      'how_time': [],
      'where': []
    }
    
    self.ignore_ids = []
    self.search_params = []
    self.asked_category = []
    

  # 名詞から5W1H情報を推定
  def __guess_key(self, value):
    result = []
    for key in self.params.keys():
      if key == 'what': continue
      result.append([key, len(self.session.query(Knowledge).filter(getattr(Knowledge, key).like("%%%s%%" % value)).all())])
    
    result.sort(key=itemgetter(1), reverse=True)
    
    if result[0][1] == 0:
      return 'what'
    else:
      return result[0][0]
    
    
  # パラメータのリセット
  def reset_params(self):
    self.params = {
      'what': [],
      'when_time': [],
      'when_day': [],
      'who': [],
      'how_time': [],
      'where': []
    }
    self.search_params = []
    

  """
  パラメータのセット/更新
  params = {
    'what': ['西野', '講堂', '講義'],
    'when_time': [],
    'when_day': [],
    'who': ['西野'],
    'how_time': [],
    'where': [],
    'category': 'where'
  }
  各形式が違えば例外（TypeError,ValueError）を投げるので例外処理してください
  """
  def set_params(self, params):
    if not isinstance(params, dict): raise TypeError('不正な引数')

    for key in self.params.keys():
      if key in params:
        if params[key] == None: continue
        if isinstance(params[key], list): 
          for item in params[key]:
            if item and item != 'null' and item not in self.params[key]:
              self.params[key].append(item)
        else:
          raise ValueError('%sはlistで渡してください' % key)
      else:
        raise ValueError('%sが存在しません' % key)
      
      
    for key, values in self.params.items():
      idx = 0
      while idx < len(values):
        value = values[idx]
        if key == 'what':
          guessed_key = self.__guess_key(value)
          item = {'key': guessed_key, 'value': value}
          if guessed_key != 'what':
            self.params[guessed_key].append(value)
            self.params['what'].remove(value)
          else:
            idx += 1;
        else:
          item = {'key': key, 'value': value}
          idx += 1;
        if item not in self.search_params: self.search_params.append(item)
      
    if 'category' in params:
      self.category = params['category']
    else:
      raise ValueError('categoryが存在しません')
    pprint(self.search_params)

  # 検索除外対象をセット
  def set_ignore(self, data):
    if isinstance(data, list):
      for item in data:
        if 'data' in item: item = item['data']
        self.ignore_ids.append(item['id'])
    else:
      if 'data' in data: data = data['data']
      self.ignore_ids.append(data['id'])
    

  # 検索除外対象をリセット
  def reset_ignore(self):
    self.ignore_ids = []


  # 検索クエリの生成
  def __generate_queries(self):
    pattern = []
    queries = []
    n = len(self.search_params)

    for i in range(1, pow(2, n)):
      s = "%0" + str(n) + "d"
      pattern.append(s % int(format(i, 'b')))

    for idx, i in enumerate(pattern):
      query = self.session.query(Knowledge)
      count = 0
      for j, v in enumerate(list(i)[::-1]):
        if v == "1" :
          query = query.filter(getattr(Knowledge, self.search_params[j]['key']).like("%%%s%%" % self.search_params[j]['value']))
          if len(self.ignore_ids): query = query.filter(not_(Knowledge.id.in_(self.ignore_ids)))
          count += 1
      if count: queries.append({'query': query, 'count': count, 'all_and': int(idx + 1 == len(pattern))})

#    query = self.session.query(Knowledge)
#    if self.mode == self.MODE_STR['and']: # AND検索
#      for key in self.params.keys():
#        print('AND')
#        if self.params[key] and self.params[key] != 'null':
#          query = query.filter(getattr(Knowledge, key) == self.params[key])
#    elif self.mode == self.MODE_STR['or']: # OR検索
#      or_str = (Knowledge.id == '')
#      for key in self.params.keys():
#        print('OR')
#        if self.params[key] and self.params[key] != 'null':
#          or_str |= getattr(Knowledge, key) == self.params[key]
#      query = query.filter(or_str)

  
    return queries


  # 結果の辞書化
  def to_dict(self, result):
    return list(map(lambda n:n.to_dict(), result)) # 結果を辞書に変換

  """
  検索の実行
  全条件を使用してマッチしたかどうかを示す'all_and'、辞書形式の情報を要素とする'data'と、
  信頼度を表す'reliability'を要素として持つ辞書を列挙するリストを返します。
  何も結果がなければ空のリストを返します。
  [{'all_and': 1,
    'data': {'created_at': None,
             'how_time': '10時間',
             'id': 7,
             'title': '剣道部のフライドチキン',
             'updated_at': None,
             'what': '剣道部のフライドチキン',
             'when_day': '17',
             'when_time': '10',
             'where': '広場',
             'who': '剣道部'},
    'reliability': 4.0},
   {'all_and': 0,
    'data': {'created_at': None,
             'how_time': '10時間',
             'id': 6,
             'title': 'ラグビー部の唐揚げ',
             'updated_at': None,
             'what': 'ラグビー部の唐揚げ',
             'when_day': '17',
             'when_time': '10',
             'where': '広場',
             'who': 'ラグビー部'},
    'reliability': 0.3333333333333333}]
  """
  def search(self):
    results = []
    queries = self.__generate_queries()
    try:
      for query in queries:
        result = self.to_dict(query['query'].all())
        results.extend(list(map(lambda n:{'data': n, 'count': query['count'], 'all_and': query['all_and']}, result)))
    
#        if len(result) == 0:
#          self.mode = self.MODE_STR['or']
#          query = self.__generate_query()
#          result = self.to_dict(query.all())
        
    except:
      raise Exception('データベースに接続できません' % key)
    
    results_uniq = []
    data = []
    reliabilities = []
    all_and_list = []
    for result in results:
      add_ok = True
      if self.category == 'when':
        for param in self.params['when_day']:
          if result['data']['when_day'] and param in result['data']['when_day']:
            add_ok = False
            break
        for param in self.params['when_time']:
          if result['data']['when_time'] and param in result['data']['when_time']:
            add_ok = False
            break
      else:
        for param in self.params[self.category]:
          if result['data'][self.category] and param in result['data'][self.category]:
            add_ok = False
            break
      if result['data'] not in data:
        data.append(result['data'])
        if add_ok:
          reliabilities.append(result['count'])
          all_and_list.append(result['all_and'])
        else:
          reliabilities.append(0)
          all_and_list.append(0)
      else:
        idx = data.index(result['data'])
        if add_ok:
          reliabilities[idx] += result['count']
          all_and_list[idx] += result['all_and']
      
    
    for idx, item in enumerate(data):
      results_uniq.append({'data': item, 'reliability': reliabilities[idx] / len(self.search_params), 'all_and': all_and_list[idx]})
      
    results_uniq.sort(key=itemgetter('reliability'), reverse=True)
    
    for idx, item in enumerate(results_uniq):
      if idx == 5:
        print('（6件目以降省略）')
        break
      pprint(item)
      
    return results_uniq
  
  
  # 最重要キーワードの判定
  def get_wanting_category(self):
    wanting_category = None
    if self.category == 'what':
      if self.params['where'] == [] and 'where' not in self.asked_category: wanting_category = 'where'
      elif self.params['who'] == [] and 'who' not in self.asked_category: wanting_category = 'who'
      elif self.params['when_time'] == [] and 'when_time' not in self.asked_category: wanting_category = 'when_time'
      elif self.params['when_day'] == [] and 'when_day' not in self.asked_category: wanting_category = 'when_day'
      #if self.params['how_time'] == [] and 'how_time' not in self.asked_category: wanting_category = 'how_time'
    if self.category == 'when':
      if self.params['what'] == [] and 'what' not in self.asked_category: wanting_category = 'what'
      elif self.params['where'] == [] and 'where' not in self.asked_category: wanting_category = 'where'
      elif self.params['who'] == [] and 'who' not in self.asked_category: wanting_category = 'who'
      #if self.params['how_time'] == [] and 'how_time' not in self.asked_category: wanting_category = 'how_time'
    if self.category == 'who':
      if self.params['what'] == [] and 'what' not in self.asked_category: wanting_category = 'what'
      elif self.params['where'] == [] and 'where' not in self.asked_category: wanting_category = 'where'
      elif self.params['when_time'] == [] and 'when_time' not in self.asked_category: wanting_category = 'when_time'
      elif self.params['when_day'] == [] and 'when_day' not in self.asked_category: wanting_category = 'when_day'
      #if self.params['how_time'] == [] and 'how_time' not in self.asked_category: wanting_category = 'how_time'
    if self.category == 'how_time':
      if self.params['what'] == [] and 'what' not in self.asked_category: wanting_category = 'what'
      elif self.params['where'] == [] and 'where' not in self.asked_category: wanting_category = 'where'
      elif self.params['who'] == [] and 'who' not in self.asked_category: wanting_category = 'who'
      elif self.params['when_time'] == [] and 'when_time' not in self.asked_category: wanting_category = 'when_time'
      elif self.params['when_day'] == [] and 'when_day' not in self.asked_category: wanting_category = 'when_day'
    if self.category == 'where':
      if self.params['what'] == [] and 'what' not in self.asked_category: wanting_category = 'what'
      elif self.params['who'] == [] and 'who' not in self.asked_category: wanting_category = 'who'
      elif self.params['when_time'] == [] and 'when_time' not in self.asked_category: wanting_category = 'when_time'
      elif self.params['when_day'] == [] and 'when_day' not in self.asked_category: wanting_category = 'when_day'
      #if self.params['how_time'] == [] and 'how_time' not in self.asked_category: wanting_category = 'how_time'
    if self.category == 'how':
      if self.params['what'] == [] and 'what' not in self.asked_category: wanting_category = 'what'
      elif self.params['where'] == [] and 'where' not in self.asked_category: wanting_category = 'where'
      elif self.params['who'] == [] and 'who' not in self.asked_category: wanting_category = 'who'
      elif self.params['when_time'] == [] and 'when_time' not in self.asked_category: wanting_category = 'when_time'
      elif self.params['when_day'] == [] and 'when_day' not in self.asked_category: wanting_category = 'when_day'
      #if self.params['how_time'] == [] and 'how_time' not in self.asked_category: wanting_category = 'how_time'
    
    self.asked_category.append(wanting_category)
    return wanting_category
  
  
  # 親データを返す
  def get_parent(self, parent_id):
    return self.session.query(Knowledge).filter_by(id=parent_id).one().to_dict()
