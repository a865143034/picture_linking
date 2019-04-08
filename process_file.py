#coding:utf-8
f=open('output_enwiki.txt','r')
f2=open('lass_output.txt','w')
for line in f:
    try:
        line=line.split('\t')
        line[1]=line[1].strip()
        if line[1]=='https://en.wikipedia.org/wiki/File:':
            continue
        line[1]=line[1].replace('[[File:','')
        line[1]=line[1].replace(']]','')
        line=line[0]+'\t'+line[1]+'\n'
        f2.write(line)
    except:
        continue
f.close()
f2.close()
