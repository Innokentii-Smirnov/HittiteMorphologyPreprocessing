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
doc = Document.load('{0}-sux-pos.txt'.format(CORPUS))
len(doc)


# In[6]:


segments = doc.segments
len(segments)


# In[7]:


nodes = [node for node in doc.wordforms if node.segment.lang == 'hit']
len(nodes)


# In[8]:


sum(1 for node in nodes if node.upos is None)


# ## Analytics

# In[9]:


nominals = list(filter(lambda node: node.upos == 'NOMINAL', nodes))
len(nominals)


# In[10]:


from library.iterable import group_by
by_lemma = group_by(lambda node: node.lemma, nominals)
lemmata = sorted(by_lemma)


# In[11]:


set((node.lemma, node.gloss) for node in nominals if node.gloss.islower())


# In[12]:


for node in nominals:
    if node.gloss.islower():
        if node.gloss == 'darin':
            node.upos = 'ADV'
        else:
            node.upos = 'ADJ'


# In[13]:


nominals = list(filter(lambda node: node.upos == 'NOMINAL', nodes))
len(nominals)


# In[14]:


for node in nominals:
    if node.gloss in {'Gottesmutter', 'Tag (vergöttlicht)'}:
        node.upos = 'DN'
    else:
        node.upos = 'NOUN'


# In[15]:


set((node.form, node.gloss) for node in nominals if node.lemma =='_')


# In[16]:


set((node.lemma, node.gloss) for node in nominals)


# In[17]:


sum(1 for node in nodes if node.upos == 'NOMINAL')


# In[18]:


from collections import Counter
Counter(node.xpos for node in nodes if node.upos == 'PREP')


# In[19]:


for node in nodes:
    if node.upos == 'PREP':
        node.xpos = None


# ## Saving

# In[20]:


os.chdir(direct)
doc.save('{0}-hit-pos.txt'.format(CORPUS))

