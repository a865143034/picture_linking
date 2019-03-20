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
#nlp = StanfordCoreNLP('http://202.120.38.146:8098')

def ner(text):
    nlp = StanfordCoreNLP('http://202.120.38.146:8098/')
    #nlp = StanfordCoreNLP('http://localhost:8098/')
    output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,ner',
        'outputFormat': 'json',
    })
    return output['sentences']

def trim(text):
    entitys=ner(text)
    lst=[]
    for entity in entitys:
        dic1=entity['entitymentions']
        all_obj=entity['tokens']
        for obj1 in dic1:
            tmp=obj1['text']
            start=obj1['tokenBegin']
            end=obj1['tokenEnd']
            all_obj[start]={'originalText':tmp}
            for num in range(start+1,end):
                all_obj[num]=""
        for obj in all_obj:
            if not obj:continue
            lst.append(obj['originalText'])
    return lst



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
        dic=trim(text)
        for obj in dic:
            wrd=obj.lower()
            if wrd in m:
               t1=func(m[wrd])
               if not t1:
                  ans+=obj+" "
                  continue
               ans_tmp="<a href=\'"+t1+"\' class=\'hyper\' target=\'_blank\'>"+obj+"</a>"
               ans+=ans_tmp+" "
            else:
               ans+=obj+" "
        return HttpResponse(
            json.dumps({
		"ans":ans,
            }))



