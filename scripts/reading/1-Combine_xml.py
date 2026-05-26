#!/usr/bin/env python
# coding: utf-8

# ### Imports

# In[1]:


import os
import sys

try:
    from google.colab import drive
    drive.mount('/content/drive')
    sys.path.insert(1, "/content/drive/MyDrive/3-python-packages")
except ModuleNotFoundError:
    print(sys.path[1])


# In[2]:


from hit_morph.constants import CORPUS, VERSION, HM, HC
print(CORPUS, VERSION, HM, HC, sep='\n')


# ### Multiple files

# In[9]:


from bs4 import BeautifulSoup, Tag
from tqdm.auto import tqdm
from unicodedata import normalize


# In[5]:


CURRENT = os.getenv('CURRENT')


# In[6]:


from os import path
source = os.getenv('INPUT')
#source = 'C:/Corpora/Hittite/HFR/e2-colaid'
assert path.exists(source)


# In[7]:


walk = list(os.walk(source))


# In[10]:


soup = BeautifulSoup('<corpus name="{0}" version="{1}"></corpus>'.format(CORPUS, VERSION), 'xml')
corpus = soup.corpus
tq = tqdm(walk)


# In[11]:


for dirpath, dirnames, filenames in tq:
    for filename in filenames:
        if filename.endswith('.xml') and not filename.endswith('_trscr.xml'):
            fullname = path.join(dirpath, filename)
            with open(fullname, 'r', encoding='utf-8') as fin:
                doc = fin.read()
            doc = normalize('NFKC', doc)
            soup = BeautifulSoup(doc, 'xml')
            text_tag = soup.AOxml.body.div1.find('text')
            text_tag['path'] = path.relpath(dirpath, source)
            text_tag['file'] = filename.removesuffix('.xml')
            corpus.append(text_tag)


# In[12]:


print('texts: ', len(list(corpus('text'))))
print('pars: ', len(list(corpus('parsep'))))
print('sents: ', len(list(corpus('clb'))))
print('words: ', len(list(corpus('w'))))


# In[13]:


len(list(corpus('w'))) / len(list(corpus('parsep')))


# Lastly:
# texts:  8260
# pars:  28743
# sents:  95713
# words:  533284
# Formerly:
# texts:  8266
# pars:  28813
# sents:  99314
# words:  535564

# In[14]:


string = str(corpus)


# In[15]:


print(string[1000:2000])


# In[16]:


from os import path
target_dir = os.getenv('OUTPUT')
os.makedirs(target_dir, exist_ok=True)


# In[17]:


with open(path.join(target_dir, 'Combined.xml'), 'w', encoding='utf-8') as fout:
    fout.write(string)


# In[13]:


#with open(path.join(target_dir, 'Combined.xml'), 'r', encoding='utf-8') as fin:
#    new_string = fin.read()


# In[14]:


#new_soup = BeautifulSoup(new_string, 'xml')


# In[15]:


#for tag in 'text,parsep,clb,w'.split(','):
#    print(len(new_soup(tag)))


# In[18]:


def count_substrings(substring: str, string: str) -> int:
    count = 0
    for i in range(len(string) - len(substring)):
        if string[i:i+len(substring)] == substring:
            count += 1
    return count


# In[19]:


altogether = count_substrings('mrp0sel', string)
altogether


# In[20]:


empty = count_substrings('mrp0sel="???"', string)
empty


# In[21]:


100 * empty / altogether


# In[22]:


words = corpus('w')
len(words)


# In[23]:


empty = list(filter(lambda word: 'opt0sel' in word.attrs and word['opt0sel'].strip() == '', words))
len(empty)


# In[24]:


for w in empty:
    print(w.parent['path'], w.parent['file'])
    print(w['exp'])


# In[ ]:




