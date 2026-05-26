#!/usr/bin/env python
# coding: utf-8

# ## Loading

# ### Imports

# In[2]:


import os
import sys
from os import path

try:
    from google.colab import drive
    drive.mount('/content/drive')
    get_ipython().run_line_magic('env', 'HM=/content/drive/MyDrive/2-Hittite-morphology')
    folder = '/content/drive/MyDrive'
    sys.path.insert(1, path.join(folder, '3-python-packages'))
except ModuleNotFoundError:
    print(os.environ["HM"])
    print(sys.path[1])
    folder = 'G:/Мой диск'

hm = os.getenv('HM')
assert path.exists(hm)


# In[3]:


from hit_morph.constants import CORPUS, VERSION
print(CORPUS, VERSION)


# In[4]:


from functools import partial
from library.iterable import group_by, group_by_many, modify_values, pi, chain_seq, composition, compone


# ### Reading

# In[5]:


direct = os.getenv('OUTPUT')
assert path.exists(direct)
os.chdir(direct)


# In[6]:


from hit_morph.struct.document import Document
doc = Document.load('{0}-normalized-strings.txt'.format(CORPUS))
len(doc)


# In[7]:


segments = doc.segments
len(segments)


# In[8]:


nodes = doc.wordforms
len(nodes)


# ## Preprocessing

# In[9]:


import re
transliteration_pattern = re.compile(r'(<d>[^<>]+</d>)?[^<>]+(<d>[^<>]+</d>)?[^<>]*')


# In[10]:


def preprocess_det(det: str | None):
    if det is None:
        return det
    else:
        det = det.removeprefix('<d>')
        det = det.removesuffix('</d>')
        return det


# In[11]:


set(segment.translit for segment in segments if '〈' in segment.translit)


# In[12]:


from hit_morph.struct.segment import Segment

def set_determinatives(segment: Segment):
    if segment.translit is not None:
        translit = segment.translit.split('˽')[0].replace('<d></d>','')
        translit = translit.replace('〈', '')
        translit = translit.replace('〉', '')
        matched = transliteration_pattern.fullmatch(translit)
        if matched is not None:
            predet, postdet = matched.groups()
            segment.predet = preprocess_det(predet)
            segment.postdet = preprocess_det(postdet)


# In[13]:


for segment in segments:
    try:
        set_determinatives(segment)
    except:
        print(segment.sentence)
        raise


# ## Final analytics

# In[14]:


for segment in segments:
    if segment.predet == 'LÚ.MEŠLÚ':
        segment.predet = 'LÚ.MEŠ'


# In[15]:


from collections import Counter
Counter(segment.predet for segment in segments)


# In[16]:


Counter(segment.postdet for segment in segments)


# In[17]:


predets = set(segment.predet for segment in segments)
set(segment.translit for segment in segments if segment.postdet in predets - {None})


# ## Saving

# In[18]:


doc.save('{0}-determinatives.txt'.format(CORPUS))


# ## Determinatives

# In[19]:


transl = []
for node in segments:
    transl.append(node.translit)


# In[20]:


transl_pattern = re.compile(r'(<d>[^<>]+</d>)?[^<>]+(<d>[^<>]+</d>)?[^<>]*')
err = set()
for trans in transl:
    word = trans.split('˽')[0].replace('<d></d>','')
    if transl_pattern.fullmatch(word) is None:
        err.add(trans)


# In[21]:


for x in err:
    print(x)


# ## Analytics

# In[22]:


def extract(func):
    res = set()
    for node in segments:
        res.add(func(node))
    return res


# In[23]:


extract(lambda node: node.predet)


# In[24]:


extract(lambda node: node.postdet)


# In[25]:


gramm_forms = set(node.xpos for node in nodes)


# In[26]:


from hit_morph.parsing.gramm_forms import parse_gramm_form
for gf in gramm_forms:
    try:
        parse_gramm_form(gf)
    except:
        print(gf)


# In[ ]:




