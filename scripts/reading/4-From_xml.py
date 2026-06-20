#!/usr/bin/env python
# coding: utf-8

# ### Imports

# In[1]:


import os
import sys

try:
    from google.colab import drive
    drive.mount('/content/drive')
    get_ipython().run_line_magic('env', 'HM=/content/drive/MyDrive/2-Hittite-morphology')
    sys.path.insert(1, "/content/drive/MyDrive/3-python-packages")
except ModuleNotFoundError:
    print(os.environ["HM"])
    print(sys.path[1])


# In[2]:


from hit_morph.constants import CORPUS, VERSION, HM
print(CORPUS, VERSION, HM)


# ### Library

# In[3]:


import re
from re import Pattern
import os
from os import path
from typing import Callable
from bs4 import BeautifulSoup, Tag
from tqdm.auto import tqdm
from unicodedata import normalize


# In[4]:


from importlib import reload
import hit_morph
reload(hit_morph)
import hit_morph.corrections
reload(hit_morph.corrections)
import hit_morph.parsing.analysis
reload(hit_morph.parsing.analysis)
import hit_morph.struct.morpholex
reload(hit_morph.struct.morpholex)
import hit_morph.struct.segment
reload(hit_morph.struct.segment)


# In[5]:


from hit_morph.struct.inflecting import Inflecting
from hit_morph.struct.morpholex import Morpholex
from hit_morph.struct.encl_chain import EnclChain
from hit_morph.parsing.analysis import parse_analysis
from hit_morph.parsing.gramm_forms import preprocess_gramm_form, conv
from hit_morph.corrections import gramm_form_corr
from gen_morph.exceptions import CannotParseMorpholex, CannotParseFormSet, CannotParseGrammForm


# In[6]:


import library
from os import path
direct = os.getenv('OUTPUT')
assert path.exists(direct)
os.chdir(direct)


# ### Loading

# In[7]:


from library.read import read_text
text = read_text(path.join(direct, 'Reduced.xml'))
soup = BeautifulSoup(text, 'xml')
sents = soup('sent')
print(len(sents))


# In[8]:


for w in soup.find('sent')('w'):
    print(w)


# ### Processing single sentence

# In[9]:


from hit_morph.struct.sentence import Sentence
from hit_morph.struct.document import Document


# In[10]:


sent_tags = soup('sent')


# In[11]:


from functools import partial
from hit_morph.check.wordform import check_wordform
check = partial(check_wordform, trans='exp', mrp='opt0sel')
sent_tag = sent_tags[155]
for x in sent_tag('w'):
    print(str(x))
    print(check(x))
    print()


# In[12]:


sent = Sentence.from_tag(sent_tag)


# In[16]:


from hit_morph.struct.segment import Segment
r = repr(sent.segments[0])
print(r)


# In[17]:


print(Segment.from_string(r))


# In[18]:


r = repr(sent)
print(r)


# In[19]:


Sentence.from_string(r)


# In[20]:


repr(Sentence.from_string(r)) == r


# ### Multiple files

# In[21]:


document = Document()
tq = tqdm(sent_tags)


# In[22]:


for sent_tag in tq:
    try:
        sent = Sentence.from_tag(sent_tag)
        if len(sent) == 0:
            print('Empty!')
        document.append(sent)
    except CannotParseGrammForm as exc:
        print(exc)
        print()


# In[23]:


s = document[7]
s.metadata


# In[24]:


segm = s.segments[0]


# In[25]:


segm


# In[26]:


for x in segm.get_elements():
    print(type(x), x)


# In[27]:


document[2]


# In[28]:


err = []

for i, sent in enumerate(document):
    try:
        r = repr(sent)
        assert repr(Sentence.from_string(r)) == r
    except:
        err.append(i)
        print(i)
        raise

len(err)


# In[29]:


from hit_morph.struct.selection import SelectionList
SelectionList.from_string('')


# In[30]:


r = repr(document)
print(r[:200])


# In[31]:


d = Document.from_string(r)
repr(d) == r


# In[32]:


filename = '{0}.txt'.format(CORPUS)
document.save(filename)


# In[33]:


doc = Document.load(filename)


# In[34]:


repr(doc) == repr(document)


# In[35]:


print(len(document))
