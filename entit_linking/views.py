from django.http import HttpResponse
from django.shortcuts import render
import json
import gensim
import nltk
from lxml import etree

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

def parse_(html):
    try:
        html = etree.HTML(html)
        img= html.xpath('//*[@id="file"]/a/img/@src')[0]
        img="https:"+img
        return img
    except:
        return 0


def func(url):
    htm=getHTMLText(url)
    ans=parse_(htm)
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



import queue
import threading
import time

class myThread (threading.Thread):
    def __init__(self, threadID, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.q = q
    def run(self):
        self.process_data(self.q)
    @staticmethod
    def process_data(q):
        while not exitFlag:
            queueLock.acquire()
            if not workQueue.empty():
                data = q.get()
                queueLock.release()
                tmp_ans=func(data[1])
                ans_queue.put((data[0],tmp_ans))
            else:
                queueLock.release()
            time.sleep(0.1)

def thread_caw(urlList):
    global exitFlag
    global workQueue
    global queueLock
    global ans_queue
    exitFlag=0
    workQueue=queue.Queue()
    queueLock=threading.Lock()
    ans_queue=queue.Queue()
    threadnum=20
    threads = []

    for threadID in range(threadnum):
        thread = myThread(threadID, workQueue)
        thread.start()
        threads.append(thread)

    queueLock.acquire()
    for word in urlList:
        workQueue.put(word)
    queueLock.release()

    while not workQueue.empty():pass

    exitFlag = 1
    for t in threads:
        t.join()


def get_img_dic(url_list):
    thread_caw(url_list)
    dic_={}
    while not ans_queue.empty():
        data=ans_queue.get()
        dic_[data[0]]=data[1]
    return dic_

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
        nxt_list=[]
        for obj in dic:
            wrd=obj.lower()
            if wrd in m:
                nxt_list.append((wrd,m[wrd]))
        dic_=get_img_dic(nxt_list)
        for obj in dic:
            wrd=obj.lower()
            if wrd in m:
               t1=dic_[wrd]
               if not t1:
                  ans+=obj+" "
                  continue
               ans_tmp="<a href=\'"+t1+"\' class=\'hyper\' target=\'_blank\'>"+obj+"</a>"
               ans+=ans_tmp+" "
            else:
               ans+=obj+" "
        return HttpResponse(
            json.dumps({
                "ans": ans,
            }))



