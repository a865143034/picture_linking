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

from pycorenlp import StanfordCoreNLP
def ner(text):
    nlp = StanfordCoreNLP('http://localhost:8098')
    output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,ner',
        'outputFormat': 'json',
    })
    #print(output['sentences']['entitymentions'])
    return output['sentences'][0]['entitymentions']

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
        dic=ner(text)
        for i in dic:
            tmp=i['text']
            wrd=tmp.lower()
            if wrd in m:
               t1=func(m[wrd])
               if not t1:continue
               ans_tmp="<a href=\'"+t1+"\' class=\'hyper\' target=\'_blank\'>"+tmp+"</a>"
               text=text.replace(tmp,ans_tmp)
        return HttpResponse(
            json.dumps({
		"ans":text,
            }))



