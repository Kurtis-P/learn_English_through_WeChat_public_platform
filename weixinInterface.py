# -*- coding: utf-8 
#调用第三方库
import hashlib
import web
import lxml
import time
import os
import urllib2,json
from lxml import etree
import random
import requests
import re

#建立类实现功能
class WeixinInterface:
	
	#初始化类
    def __init__(self):
        self.app_root = os.path.dirname(__file__)
		#这是xml文件的目录
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)

    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
		
        #自己的token，处于隐私做了处理
        token="********"
		
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
		
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr
    
	#报文回复
    def POST(self):
		#获得post来的数据
        str_xml = web.data() 
		#进行XML解析
        xml = etree.fromstring(str_xml)
		#获得用户所输入的内容
        content=xml.find("Content").text
        msgType=xml.find("MsgType").text
		#获得发送者ID
        fromUser=xml.find("FromUserName").text
		#获得接受者ID
        toUser=xml.find("ToUserName").text
		
		#对所获内容进行分类处理
		#使用if语句而不使用if...else语句的原因是新浪云对于else的支持有问题，会偶发报错（待进一步判断）
        if(u'新闻' in content):
            if(u'文字' in content):
                try:
					news,pics,title,new_url=self.getNews()
                    news[0]=new[0].replace("\'","’")
					#回复标准xml信息，这个为文字xml
                    return self.render.reply_text(fromUser,toUser,int(time.time()),news[0])
                except:
                    cont=u'er101'
					#出错报错并返回错误代码
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"服务器开小差了:( \n请重新回复关键字！ \n"+cont)
            if(u'文字' not in content):
                try:
					#回复标准xml信息，这个为图文信息xml
                    news,pics,title,new_url=self.getNews()
                    title=title.replace("\'","’")
                    return self.render.reply_complex(fromUser,toUser,int(time.time()),title,title,pics,new_url)
                except:
					#出错报错并返回错误代码
                    cont=u'er102'
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"服务器开小差了:( \n请重新回复关键字！ \n"+cont)
        
		if(u'单词' in content):
            try:
                word=str(self.words())
                word=word.strip()
                word=word.replace("\'","’")
				#回复标准xml信息，这个为文字xml
                return self.render.reply_text(fromUser,toUser,int(time.time()),word)
            except:
                cont=u'er103'
				#回复标准xml信息，这个为文字xml
                return self.render.reply_text(fromUser,toUser,int(time.time()),u"服务器开小差了:( \n请重新回复关键字！ \n"+cont)
        
		if(u'单词' not in content) and (u'新闻' not in content):
            #回复标准xml信息，这个为文字xml
			#作为提示信息出现，保证每次输入均有回复
			cont=u'回复【新闻】或【文字新闻】获取最新英文新闻。\n回复【单词】获取托福单词\n'
            return self.render.reply_text(fromUser,toUser,int(time.time()),cont)
	
	#获取网页
    def getWebpage(self,url,kw):
        
		headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3;WOW64) AppleWebKit/537.36(KHTML,like Gecko) Chrome/57.0.2987.110 Safari/573.36','referer':''#
        }
		
        try:
            r=requests.get(url,headers=headers,\
                                   params=kw,timeout=30)
            #print(r.status_code)
            r.raise_for_status()
            r.encoding=r.apparent_encoding
            return r.text
        except:
            return 'error'

	#获取新闻
    def getNews(self):
        kw={'wd':'python requests'}
        url=['http://www.chinadaily.com.cn/china']
		#调用getWebpage函数下载网页html文件
        s=self.getWebpage(url[0],kw)
		#使用正则表达式提取目标新闻地址
        match=re.findall('<a target="_top" shape="rect" href=.+?</a>',s)
        i=0
        res=[]
        res_url=[]
        res_name=[]
        for x in match:
            if i>20:
				#运用总结规则筛选有效地址
                if ('img' not in x)and('font' not in x)and('span' not in x):
                    res.append(str(x))
					
            i+=1
			#设置结束条件
            if i ==150:
                break
		
		#处理字符串并将超链接与文章标题保存
        for x in res:
            x=x.split('\"')
            num=x[6].find('</a>')
            if len(x[6])>25:
                res_url.append(x[5])
                res_name.append(x[6][1:num])
		
        #将保存下来的文档随机抽取一个进行后续信息收集
        num=random.randint(0,len(res_url)-1)
        s=self.getWebpage(res_url[num],kw)
        title=res_name[num]
        new_url=res_url[num]
        
		#收集新闻内容
        match=re.findall('<p>.+?</p>',s)#正则表达式一
        news=[]
        for x in match:
            if ('<a>' not in x):
                x=x[3:]
                x=x.replace('</p>','\n')
                news.append(x)
		
        match=re.findall('<figcaption.+?</figcaption>',s)#正则表达式二
        for x in match:
            if ('<a>' not in x):
                #print(x)
                x.replace('<','《')
                x.replace('>','》')
                x.replace('\'','’')
                x=x.split('》')
                x=x[1]
                x=x.replace('</figcaption','\n')
                news.append(x)
        
		#获取新闻中图片地址
        match=re.findall('<img src=.+?data-mimetype',s)
        for x in match:
            x=x.split('\"')
            pics=x[1]
			
        return news,pics,title,new_url
	
	#读取data.txt文件获取托福单词
    def words(self):
        f=open('data.txt','r')
    	data=f.readlines()
        num=f.tell()
		#随机选取一个
        num=random.randint(0,num-100)
        f.seek(num)
		
        data=f.readline()
        data=f.readline()
        if data=='\n':
            data=f.readline()
        f.close()
		
        data=data.split('.')
        data=data[1:]
        data=''.join(data)
        return data