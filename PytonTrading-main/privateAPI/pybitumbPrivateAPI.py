"""
빗썸의 private API를 사용하기 위해 발급받은 키와 시크릿을 넣고 호출
"""

import pybithumb
from privateAPI.secret import *

api_key = my_api_key
api_secret = my_api_secret

pybithumbPrivateAPI = pybithumb.Bithumb(api_key, api_secret)
