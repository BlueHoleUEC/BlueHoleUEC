# coding:utf-8
#IBM Watson　API　のNLCを呼び出す

#python のバージョン指定：python 3.5.0

from watson_developer_cloud import NaturalLanguageClassifierV1
from watson_developer_cloud import NaturalLanguageClassifierV1 as NaturalLanguageClassifier


#5w1h1i1c_v.5:ff18a8x156-nlc-1275
#5w1h1i1c_v.5:ff18c7x157-nlc-2812
#5w1h1i1c_v.7:ff1c34x160-nlc-4342
#5w1h1i1c_v.8:ff1c2bx159-nlc-4926
#5w1h1i1c_v.9:cede31x166-nlc-1812
#5w2h_v.10:cedd09x164-nlc-4477

def nlc_0(text):
	#NLC読み込みのためのアカウント情報
	natural_language_classifier = NaturalLanguageClassifierV1(
	  #username='f36f2174-aae0-40a0-8b8c-6d138726727d',
	  #password='YW5Yu1VBXdKh'
	  #新たに、アカウント作成必要

	  )
#watson　ID:ff1c2bx159-nlc-4926
	print('----- Watson NLC　からの応答待ち -----')
	res = natural_language_classifier.classify('cedd09x164-nlc-4477', text)
	ans = res["top_class"]
	return ans