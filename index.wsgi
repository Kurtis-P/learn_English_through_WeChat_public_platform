# coding: UTF-8
import os
import sys
import sae
import web

from weixinInterface import WeixinInterface

urls = (
'/weixin','WeixinInterface'
)

app_root = os.path.dirname(__file__)
#安装第三方库
sys.path.insert(0, os.path.join(app_root, 'requests.zip'))
sys.path.insert(0, os.path.join(app_root, 'urllib3.zip'))
sys.path.insert(0, os.path.join(app_root, 'chardet.zip'))
sys.path.insert(0, os.path.join(app_root, 'certifi.zip'))
sys.path.insert(0, os.path.join(app_root, 'idna.zip'))

#获取xml所在目录
templates_root = os.path.join(app_root, 'templates')
render = web.template.render(templates_root)

#格式代码
app = web.application(urls, globals()).wsgifunc()        
application = sae.create_wsgi_app(app)