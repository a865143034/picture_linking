from django.http import HttpResponse
from django.shortcuts import render
import json
import gensim
import nltk


import requests
from bs4 import BeautifulSoup
import bs4
headers = {
    'User-Agent':'Chrome/68.0.3440.106'
}
def getHTMLText(url):
    try:
        r=requests.get(url,headers=headers)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return ''

def get_img(html):
    try:
        soup=BeautifulSoup(html,'lxml')
        node=soup.find('div', {'class': 'fullImageLink','id':'file'})
        img_node = node.find('img')
        if not img_node:return ""
        img=img_node['src']
        img="https:"+img
        return img
    except:
        return ""

def func(url):
    htm=getHTMLText(url)
    ans=get_img(htm)
    return ans



def hello(request):
    return render(request,'index.html')

def linking(request):
    f=open('output_enwiki.txt','r')
    m={}
    for line in f:
        try:
           line=line.strip().split('\t')
           m[line[0].lower()]=line[1]
        except:
           continue
    if request.method == "POST":
        ans=""
        text=request.POST['text']
        words = nltk.word_tokenize(text)
        for word in words:
            wrd=word.lower()
            if wrd in m:
               t1=func(m[wrd])
               if not t1:
                  ans+=wrd+" "
                  continue
               tmp="<a href=\'"+t1+"\' class=\'hyper\' target=\'_blank\'>"+wrd+" "+"</a>"
               ans+=tmp
            else:
               ans+=wrd+" "	
        return HttpResponse(
            json.dumps({
                "text":text,
		"ans":ans,
            }))



