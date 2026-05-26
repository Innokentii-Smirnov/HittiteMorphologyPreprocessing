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
    drive_dir = '/content/drive/MyDrive'
except ModuleNotFoundError:
    print(os.environ["HM"])
    print(sys.path[1])
    drive_dir = 'G:/Мой диск'


# In[2]:


from hit_morph.constants import CORPUS, VERSION, HM
print(CORPUS, VERSION, HM)


# ### Loading

# In[3]:


from os import path
source = os.getenv('OUTPUT')
path.exists(source)


# In[4]:


from library.dm import DM
from library.read import read_text
with DM(source):
    contents = read_text('{0}.xml'.format(CORPUS))


# In[5]:


from bs4 import BeautifulSoup, Tag
from importlib import reload


# In[6]:


soup = BeautifulSoup(contents, 'xml')
sentences = soup('sent')
sentences[4]


# In[7]:


len(sentences)


# In[8]:


sum(len(sentence('w')) for sentence in sentences)


# In[9]:


index = 248
sentences[index]('w')


# In[10]:


len(sentences[index]('w'))


# ### Parsing

# In[11]:


import hit_morph.parsing.analysis
reload(hit_morph.parsing.analysis)


# In[12]:


from hit_morph.check.wordform import check_wordform, Result


# In[13]:


# No longer used
def is_correct(w: Tag):
    checked = check_wordform(w, 'exp', 'opt0sel')
    return checked is None or checked == Result.NOTE or checked == Result.EMPTYSEL


# In[14]:


from library.iterable import group_by, modify_values
from functools import partial
check = partial(check_wordform, trans='exp', mrp='opt0sel')
grouped = group_by(check, soup('w'))
modify_values(len, grouped)


# In[15]:


from random import choices
choices(grouped[Result.DELIN], k=10)


# In[16]:


chs = choices(grouped[Result.OTHER], k=20)
chs


# In[17]:


chs[-1].parent.parent.parent.attrs


# In[18]:


chs[1].parent.attrs


# In[19]:


from hit_morph.struct.segment import Segment
from library.exceptions import MissingKeyException
from gen_morph.exceptions import (CannotParseWordform, CannotParseSelection,
CannotParseMorpholex, CannotParseEnclChain, CannotParseFormSet, SecondaryParsingError)

def very_correct(w: Tag) -> tuple[bool, Exception | None]:
    global cw
    checked = check(w)
    if checked == Result.NOTE:
        cw += 1
        return True, None
    else:
        try:
            wf = Segment.from_tag(w)
            segments.append(wf)
            tags.append(w)
            cw += 1
            return True, None
        except (CannotParseWordform, CannotParseSelection,
                MissingKeyException, CannotParseMorpholex,
                CannotParseEnclChain, AssertionError,
                CannotParseFormSet, SecondaryParsingError) as exc:
            return False, exc
        except:
            print(w)
            raise


# In[20]:


#import hit_morph.struct.serializable
#reload(hit_morph.struct.serializable)
import hit_morph.struct.encl_chain
reload(hit_morph.struct.encl_chain)
from hit_morph.struct.encl_chain import EnclChain
import hit_morph.struct.inflecting
reload(hit_morph.struct.inflecting)
import hit_morph.struct.segment
reload(hit_morph.struct.segment)
from hit_morph.struct.segment import Segment
from hit_morph.struct.sentence import Sentence
from hit_morph.struct.clitic_complex import CliticComplex, CliticComplexDict


# In[21]:


EnclChain('a', 'b', None).tags


# In[22]:


cw = 0
parsed = list[Tag]()
errors = list[Exception]()
segments = list[Segment]()
tags = list[Tag]()

for sent in sentences:
    sent_correct = True
    for wordform in sent('w'):
        word_correct, error = very_correct(wordform)
        if not word_correct:
            sent_correct = False
            errors.append(error)
    parsed.append(sent)

print(cw)
print(len(errors))
print(len(parsed))


# In[23]:


errs = set(map(str, errors))
len(errs)


# In[24]:


errs


# In[25]:


ambiguous = list(filter(lambda segment: len(segment[1].new_options) > 1, enumerate(segments)))
print(100 * len(ambiguous) / cw)


# In[26]:


segment = ambiguous[3]
r = repr(segment)
print(r)


# In[27]:


from hit_morph.struct.sentence import Sentence, SentenceMetadata, SegmentList
from library.iterable import pi
sent = Sentence(SentenceMetadata(*['']*4), SegmentList(pi(1)(ambiguous)[:100]))


# In[28]:


sent


# In[29]:


r = repr(sent)


# In[30]:


print(r[:100])


# In[31]:


repr(Sentence.from_string(r)) == r


# In[32]:


idx = 278
segments[idx]


# In[33]:


tags[idx]


# In[34]:


allsel = list(filter(lambda pair: 'all' in pair[1].get('mrp0sel', ''), enumerate(tags)))


# In[35]:


for idx, tag in allsel[:10]:
    print(tag)
    print()
    print(segments[idx])
    print('\n')


# In[36]:


for idx, segm in ambiguous[:100]:
    print(tags[idx])
    print()
    print(segm)
    print('\n')


# In[37]:


num = list(filter(lambda pair: any(x in pair[1].get('mrp0sel', '') for x in ['sg', 'pl']), enumerate(tags)))
len(num)


# In[38]:


for idx, tag in num[:10]:
    print(tag)
    print(segments[idx])
    print('\n')


# In[39]:


from random import choices
wencl = list(filter(lambda s: len(s[1].analyses) > 1 and s[1].analyses[0].encl_chain is not None, enumerate(segments)))
print(len(wencl))
for s in choices(wencl, k = 3):
    print(s)


# 23118

# In[40]:


secondary = list(filter(lambda error: isinstance(error, SecondaryParsingError), errors))
len(secondary)


# In[41]:


for i, error in enumerate(secondary):
    print(i, error, sep=')\t')


# In[42]:


from library.write import write_text


# In[43]:


new_soup = BeautifulSoup('<corpus name="{0}-{1}-red"></corpus>'.format(CORPUS, VERSION), 'xml')


# In[44]:


corpus = new_soup.corpus
for sent in parsed:
    try:
        if sent['langs'] != 'Hit':
            print(sent['langs'])
        text = sent.find_parent('text')
        sent['text_group'] = text['group']
        sent['text_name'] = text['name']
        corpus.append(sent)
    except:
        print(sent.prettify())
        raise


# In[45]:


len(corpus('sent'))


# 22506

# In[46]:


string = str(new_soup)


# In[47]:


from hit_morph.corrections import wordform_corr as corr


# In[48]:


for key, value in corr.corrections.items():
    string = string.replace(key, value)


# In[49]:


with DM(source):
    write_text(string, 'Reduced.xml')


# In[50]:


from collections import defaultdict
lens = defaultdict(list)
for sent in parsed:
    lens[len(list(sent('w')))].append(sent)


# In[51]:


print(sorted(lens.keys()))


# In[52]:


for w in lens[10][0]('w'):
    print(str(w))


# In[ ]:




