#!/usr/bin/env python
# coding: utf-8

# ## Loading

# ### Imports

# In[1]:


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
HM = os.getenv('RESOURCES')
assert path.exists(HM)


# In[2]:


from hit_morph.constants import CORPUS, VERSION
print(CORPUS, VERSION)


# In[3]:


from functools import partial
from library.iterable import group_by, group_by_many, modify_values, pi, chain_seq, composition, compone


# ### Reading

# In[4]:


direct = os.getenv('OUTPUT')
assert path.exists(direct)
os.chdir(direct)


# In[5]:


from hit_morph.struct.document import Document
doc = Document.load('{0}-hit-pos.txt'.format(CORPUS))
len(doc)


# In[6]:


segments = doc.segments
len(segments)


# In[7]:


nodes = doc.wordforms
len(nodes)


# ## Prepositions

# In[8]:


from collections import Counter
Counter(node.xpos for node in nodes if node.upos == 'PREP')


# In[9]:


c = Counter((node.segment.lang, node.xpos) for node in nodes if node.upos == 'PREP')
c


# In[10]:


for node in nodes:
    if node.upos == 'PREP' and node.segment.lang == 'hit':
        print(node.segment.sentence)
        node.upos = 'DN'
        node.xpos = 'D/L.SG'
        print('***')
        print(node.segment)


# In[11]:


sum(c.values())


# In[12]:


i = 0
for node in nodes:
    if node.upos == 'PREP':
        i += 1
        node.xpos = None
i


# In[13]:


from library.iterable import count
count(lambda segment: len(segment.analyses) == 0, doc.segments)


# In[14]:


set(segment.exponent for segment in doc.segments if len(segment.analyses) == 0)


# ## Adverbs

# In[15]:


c = Counter((node.segment.lang, node.xpos) for node in nodes if node.upos == 'ADV')
c


# In[16]:


i = 0
for node in nodes:
    if node.upos == 'ADV' and node.xpos is not None:
        i += 1
        adv = node
        node.xpos = None
i


# In[17]:


adv


# ## Saving

# In[18]:


os.chdir(direct)
doc.save('{0}-prep.txt'.format(CORPUS))

