#!/usr/bin/env python
# coding: utf-8

# ## Loading

# ### Imports

# In[7]:


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


# In[2]:


from hit_morph.constants import CORPUS, VERSION
print(CORPUS, VERSION)


# In[3]:


from functools import partial
from library.iterable import group_by, group_by_many, modify_values, pi, chain_seq, composition, compone


# ### Reading

# In[8]:


outdir = os.getenv('OUTPUT')
assert path.exists(outdir)
os.chdir(outdir)


# In[9]:


from hit_morph.struct.document import Document
doc = Document.load('{0}-retokenized.txt'.format(CORPUS))
len(doc)


# In[10]:


segments = doc.segments
len(segments)


# In[11]:


nodes = doc.wordforms
len(nodes)


# ## Normalization

# ### Lemmata

# In[12]:


set(node.form for node in nodes if node.lemma is None)


# In[13]:


special = 'ḫšāīūē˽áíúé°àìùèâîûêṢṬ½×\u2044'


# In[14]:


special += special.upper()
condition = lambda string: string is None or all(x.isascii() or x in special for x in string)


# In[15]:


by_lemma = group_by(lambda node: node.lemma, nodes)


# In[16]:


lemmata = set(node.lemma for node in nodes)
print(len(lemmata))
quirky = list(filter(lambda lemma: not condition(lemma), lemmata))
print(len(quirky))


# In[17]:


for lemma in quirky:
    print(repr(lemma))


# In[18]:


print(hex(ord('⁄')))
print('\u2044')


# In[19]:


print(hex(ord('⓷')))
print('\u24f7')


# In[20]:


for lemma in quirky:
    for node in by_lemma[lemma]:
        node.lemma = node.lemma.removeprefix('\xad\xad\u200c\xad')
        node.lemma = node.lemma.removeprefix('⓷')


# In[21]:


lemmata = set(node.lemma for node in nodes)
print(len(lemmata))
quirky = list(filter(lambda lemma: not condition(lemma), lemmata))
print(len(quirky))


# ### Wordforms

# In[22]:


sum(1 for segment in segments if segment.exponent is None)


# In[23]:


sum(1 for node in nodes if node.form is None)


# In[24]:


cased = 'ḫšáíúéàìùè'


# In[25]:


special = '˽ṢṬ×â\u2044' + cased + cased.upper()


# In[26]:


condition = lambda string: all(x.isascii() or x in special for x in string)


# In[27]:


by_form = group_by(lambda segment: segment.exponent, segments)


# In[28]:


forms = set(segment.exponent for segment in  segments)
print(len(forms))
quirky = list(filter(lambda form: not condition(form), forms))
print(len(quirky))


# In[29]:


for form in quirky:
    print(repr(form))


# In[30]:


print(hex(ord('⁄')))
print('\u2044')


# ## Saving

# In[31]:


doc.save('{0}-normalized-strings.txt'.format(CORPUS))


# ## Ambiguities

# In[32]:


by_form = group_by(lambda node: node.form, nodes)


# In[33]:


readings = modify_values(compone(
    partial(group_by, lambda node: (node.lemma, node.gloss)),
    partial(modify_values, composition(partial(map, lambda node: node.xpos), list))
), by_form)


# In[34]:


segments = list(readings.keys())
segments[:10]


# In[35]:


segments.sort(key=lambda segment: (-len(readings[segment]), segment), reverse=False)
segments[:10]


# In[36]:


from collections import Counter


# In[38]:


for i in range(0, 10):
    segment = segments[i]
    print('{0} ({1})'.format(segment, len(readings[segment])))
    for (lemma, gloss), forms in readings[segment].items():
        print('\t{0} \u2018{1}\u2019 ({2})'.format(lemma, gloss, len(forms)))
        for form, occurrences in Counter(forms).items():
            print('\t\t{0} ({1})'.format(form, occurrences))
    print()


# In[41]:


direct = path.join(outdir, 'Extracted')
os.mkdir(direct)


# In[42]:


filename = path.join(direct, 'Lexical ambiguities.txt')


# In[43]:


with open(filename, 'w', encoding='utf-8') as fout:
    for segment in segments:
        if len(readings[segment]) > 1:
            fout.write('{0} ({1})\n'.format(segment, len(readings[segment])))
            for (lemma, gloss), forms in readings[segment].items():
                fout.write('\t{0} \u2018{1}\u2019 ({2})\n'.format(lemma, gloss, len(forms)))
                for form, occurrences in Counter(forms).items():
                    fout.write('\t\t{0} ({1})\n'.format(form, occurrences))
            fout.write('\n')


# In[44]:


filename = path.join(direct, 'Morphological ambiguities.txt')


# In[45]:


with open(filename, 'w', encoding='utf-8') as fout:
    for segment in segments:
        if len(readings[segment]) <= 1:
            fout.write('{0} ({1})\n'.format(segment, len(readings[segment])))
            for (lemma, gloss), forms in readings[segment].items():
                fout.write('\t{0} \u2018{1}\u2019 ({2})\n'.format(lemma, gloss, len(forms)))
                for form, occurrences in Counter(forms).items():
                    fout.write('\t\t{0} ({1})\n'.format(form, occurrences))
            fout.write('\n')


# In[46]:


n_ambi = sum(1 for segment in segments if len(readings[segment]) > 1)


# In[47]:


print(n_ambi, len(segments), round(n_ambi * 100 / len(segments), 2), sep='\n')


# In[ ]:




