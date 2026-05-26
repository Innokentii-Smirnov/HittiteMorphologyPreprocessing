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
doc = Document.load('{0}-stem-classes.txt'.format(CORPUS))
len(doc)


# In[6]:


segments = doc.segments
len(segments)


# In[7]:


nodes = [node for node in doc.wordforms if node.segment.lang == 'akk']
len(nodes)


# In[8]:


sum(1 for node in nodes if node.upos == 'NOMINAL')


# ## Analytics

# In[9]:


def getform(node) -> str:
    return node.form


# In[10]:


from library.iterable import count
sum(1 for node in nodes if node.upos == 'NOMINAL')


# In[11]:


from collections import Counter
sorted(Counter((getform(node), node.lemma, node.gloss) for node in nodes if node.upos == 'NOMINAL').items())


# ## Annotation tables


# In[13]:


import pandas as pd
tables_folder = path.join(hm, 'Annotation tables')
assert path.exists(tables_folder)
os.chdir(tables_folder)
akk_main = pd.read_excel("Akkadogramme.ods", engine='odf')
akk_main.rename({'Unnamed: 3':'Postdeterminativ'}, axis='columns', inplace=True)
akk_main.rename(lambda x: x.replace(' ', '_').replace('.',''), axis='columns', inplace=True)
akk_main.head()


# In[14]:


postdeterminativ = akk_main['Postdeterminativ']
set(postdeterminativ.to_list())


# In[15]:


akk_DN = pd.read_excel("Akkadogramme_DN.ods", engine='odf')
akk_DN.rename({'Unnamed: 3':'Eigenname'}, axis='columns', inplace=True)
akk_DN.rename(lambda x: x.replace(' ', '_').replace('.',''), axis='columns', inplace=True)
akk_DN.head()


# In[16]:


eigenname = akk_DN['Eigenname']
set(eigenname.to_list())


# In[17]:


akk_GN = pd.read_excel("Akkadogramme_GN.ods", engine='odf')
akk_GN.rename({'Unnamed: 3':'Eigenname'}, axis='columns', inplace=True)
akk_GN.rename(lambda x: x.replace(' ', '_').replace('.',''), axis='columns', inplace=True)
akk_GN.head()


# In[18]:


eigenname = akk_GN['Eigenname']
set(eigenname.to_list())


# In[19]:


tables = akk_main, akk_DN, akk_GN

for table in tables:
    print(table.shape)

akkadian = pd.concat(tables)
print(akkadian.shape)


# In[20]:


wortarten = akkadian['Wortart']


# In[21]:


tags = set(akkadian['Wortart'].to_list())
print(tags)


# In[22]:


akkadian[wortarten.isna()].shape


# In[23]:


eigenname = akkadian['Eigenname']
set(eigenname.to_list())


# In[24]:


positions = wortarten.isna() & eigenname.notna()
akkadian[positions].head()


# In[25]:


akkadian.loc[positions, 'Wortart'] = akkadian['Eigenname'][positions]
akkadian[wortarten.isna()].shape


# In[26]:


akkadian[wortarten.isna()]


# ## Prepositions

# In[27]:


akkadian[wortarten == 'PROdet']


# In[28]:


akkadian[wortarten == 'CLFcas']


# In[29]:


akkadian[wortarten == 'PREP']


# In[30]:


akkadian['Wortart'][wortarten == 'CLFcas'] = 'PREP'


# In[31]:


akkadian['Wortart'][wortarten == 'PROdet'] = 'PREP'


# ## Main

# ### Complex lexicon

# In[32]:


from library.iterable import group_by, modify_values, pi, group_by_many


# In[33]:


def keyfunc(elem):
    syll = elem.Nennform
    if pd.notna(elem.konkrete_Bedeutung):
        mean = elem.konkrete_Bedeutung.split(',', maxsplit=1)[0]
        yield syll, mean
        yield syll, '({0})'.format(mean)
        if ',' in elem.konkrete_Bedeutung:
            yield syll, elem.konkrete_Bedeutung
    elif pd.notna(elem.generische_Bedeutung):
        mean = elem.generische_Bedeutung
        mean = mean.removeprefix('eine Art ')
        mean = mean.removeprefix('eine ')
        mean = mean.removeprefix('ein ')
        mean = '({0})'.format(mean)
        yield syll, mean
        yield syll, elem.generische_Bedeutung
    else:
        mean = None
        yield syll, mean


# In[34]:


complex_lexicon = group_by_many(keyfunc, akkadian.itertuples())


# In[35]:


groups = modify_values(pi(0), group_by(lambda x: len(x[1]), complex_lexicon.items()))


# In[36]:


for key, values in groups.items():
    print(key, len(values))


# In[37]:


for x in groups[2]:
    print(x)
    entries = complex_lexicon[x]
    for entry in entries:
        print(entry.Wortart)
    #assert all(entry.Wortart == entries[0].Wortart or pd.isna(entry.Wortart) for entry in entries)
    print()
    print()


# ### Simple lexicon

# In[38]:


lexicon = group_by(lambda elem: elem.Nennform, akkadian.itertuples())


# In[39]:


grouped = modify_values(pi(0), group_by(lambda x: len(x[1]), lexicon.items()))


# In[40]:


for key, values in grouped.items():
    print(key, len(values))


# In[41]:


print(grouped[2])


# In[42]:


for syll in grouped[2]:
    entries = [entry for entry in lexicon[syll] if entry.Wortart != 'VB']
    if not all(entry.Wortart == entries[0].Wortart for entry in entries):
        print(syll)
        for x in entries:
            for key, value in x._asdict().items():
                print('{0:25} {1}'.format(key, value))
            print()
            print()
        print()
        print()
        print()


# ### Akkadian part of speech tags

# In[43]:


len(nodes)


# In[44]:


nominals = [node for node in nodes if node.upos == 'NOMINAL']
len(nominals)


# In[45]:


i = 0
notfound = []
for node in nominals:
    if node.lemma in lexicon:
        i+=1
    else:
        notfound.append(node)
print(i)


# In[46]:


len(notfound)


# In[47]:


set((getform(node), node.lemma) for node in notfound)


# In[48]:


i = 0
for node in nominals:
    if node.lemma in lexicon:
        entries = lexicon[node.lemma]
        if len(entries) == 1:
            i+=1
        elif all(entry.Wortart == entries[0].Wortart for entry in entries):
            i+=1
print(i)


# In[49]:


err = []
ambi = []
i = 0
for node in nominals:
    key = (node.lemma, node.gloss)
    if key in complex_lexicon:
        entries = complex_lexicon[key]
        if len(entries) == 1:
            i+=1
        elif all(entry.Wortart == entries[0].Wortart for entry in entries):
            i+=1
        else:
            ambi.append((node, entries))
    elif node.lemma in lexicon:
        err.append((node.lemma,
                    lexicon[node.lemma][0].konkrete_Bedeutung,
                    lexicon[node.lemma][0].generische_Bedeutung,
                    node.gloss))
print(i)


# In[50]:


len(ambi)


# In[51]:


for node, entries in ambi:
    printnode(node)
    for entry in entries:
        print(entry._asdict())


# In[52]:


len(err)


# In[53]:


for (x, a, b, c), d in modify_values(len, group_by(lambda x: x, err)).items():
    print('{4:15} {0:25} {1:20} {2:20} {3}'.format(str(a), str(b), str(c), d, x))


# ### Final

# In[54]:


err = []
matching = list[tuple[object, list]]()
i = 0
for node in nominals:
    key = (node.lemma, node.gloss)
    if key in complex_lexicon:
        entries = complex_lexicon[key]
        if len(entries) == 1:
            i+=1
        elif all(entry.Wortart == entries[0].Wortart for entry in entries):
            i+=1
        else:
            raise ValueError('Ambiguity')
        matching.append((node, entries))
    elif node.lemma in lexicon:
        entries = lexicon[node.lemma]
        if len(entries) == 1:
            i+=1
        elif all(entry.Wortart == entries[0].Wortart for entry in entries):
            i+=1
        else:
            err.append((node.lemma,
                        lexicon[node.form][0].konkrete_Bedeutung,
                        lexicon[node.form][0].generische_Bedeutung,
                        node.gloss))
        matching.append((node, entries))
print(i)


# In[55]:


len(err)


# In[56]:


len(matching)


# ### Mapping

# In[57]:


counter = Counter(tuple(sorted(set(entry.Wortart for entry in entries))) for node, entries in matching)
counter


# In[58]:


len(nominals)


# In[59]:


from itertools import chain
set(
    (
        node.form,
        node.lemma,
        node.xpos,
        node.gloss,
        ' | '.join(set(entry.konkrete_Bedeutung for entry in entries))
    )
    for node, entries in matching if any(entry.Wortart == 'VB' for entry in entries)
)


# In[60]:


class writer:
    def process_tree(x):
        if not hasattr(x, 'feats'):
            x.feats = dict()
        print(x)

for node in nodes:
    node.root = node


# In[61]:


for node, entries in matching:
    if any(entry.Wortart == 'VB' for entry in entries):
        writer.process_tree(node.root)


# In[62]:


set(
    (
        node.form,
        node.lemma,
        node.xpos,
        node.gloss,
        ' | '.join(set('{0} {1}'.format(entry.konkrete_Bedeutung, entry.Wortart) for entry in entries))
    )
    for node, entries in matching if node.form == 'QA-TI'
)


# In[63]:


grouped = modify_values(pi(0), group_by(lambda x: x[1][0].Wortart, matching))


# In[64]:


set(node.gloss for node in grouped['ADJ'])


# In[65]:


set(node.xpos for node in grouped.get('QUANcar', []))


# ### Texts

# In[66]:


err = []
modified = []
i = 0
for node in nominals:
    key = (node.lemma, node.gloss)
    if key in complex_lexicon:
        entries = complex_lexicon[key]
        if len(entries) == 1:
            i+=1
        elif all(entry.Wortart == entries[0].Wortart for entry in entries):
            i+=1
        else:
            raise ValueError('Ambiguity')
    elif node.lemma in lexicon:
        entries = lexicon[node.lemma]
        if len(entries) == 1:
            i+=1
        elif all(entry.Wortart == entries[0].Wortart for entry in entries):
            i+=1
        else:
            raise ValueError('Ambiguity')
    else:
        entries = None

    if entries is not None:
        pos = entries[0].Wortart
        if pos == 'SBST' or pos == 'VB':
            pos = 'NOUN'
        if pos == 'QUANcar':
            node.upos = 'QUAN'
            node.xpos = '{0}.{1}'.format('car', node.xpos)
            #node.feats['quantype'] = 'car'
        else:
            node.upos = pos
        modified.append(node)
print(i)


# In[67]:


j = 0
for node in nodes:
    if node.upos == 'NOMINAL':
        j+=1
print(j)


# In[68]:


assert len(nominals) == i + j


# ## Checking

# In[69]:


from hit_morph.paradigm_schemata import par_schemata


# In[70]:


errs = []
odds = []

for node in modified:
    upos = node.upos.lower()
    if upos in par_schemata:
        if node.xpos.lower() not in par_schemata[upos]:
            errs.append(node)
    elif node.xpos is not None:
        odds.append(node)


# ### Errors

# In[71]:


grouped = group_by(lambda node: (node.upos, node.xpos), errs)
for (upos, xpos), values in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
    print('{0:10} {1:15} {2}'.format(upos, xpos, len(values)))


# In[72]:


pair = ('ADJ','ACC.SG')
node = grouped[pair][0]
writer.process_tree(node.root)


# In[73]:


complex_lexicon[(node.lemma, node.gloss)][0]._asdict()


# ### Oddities

# In[74]:


grouped = group_by(lambda node: (node.upos, node.xpos), odds)
for (upos, xpos), values in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
    print('{0:10} {1:20} {2}'.format(upos, xpos, len(values)))


# In[75]:


pair = ('PREP','D/L.SG')
for node in grouped.get(pair, [])[:1]:
    writer.process_tree(node.root)


# In[76]:


pair = ('PREP', 'D/L.PL')
for node in grouped.get(pair, [])[:1]:
    writer.process_tree(node.root)


# In[77]:


complex_lexicon[(node.lemma, node.gloss)][0]._asdict()


# ## Analytics

# In[78]:


from library.iterable import count
sum(1 for node in nodes if node.upos == 'NOMINAL')


# In[82]:


from collections import Counter
for ((form, lemma, gloss, det), n) in sorted(
    Counter((getform(node), node.lemma, node.gloss, node.misc['Det']) for node in nodes if node.upos == 'NOMINAL').items()
):
    print('{0:20} {1:20} {2:20} {3:6} {4}'.format(form, lemma, str(gloss), str(n), det))


# In[84]:


s = set()
for node in nodes:
    if node.upos == 'NOMINAL':
        if node.gloss is not None and node.gloss.islower():
            node.upos = 'ADJ'
        else:
            node.upos = 'NOUN'
        s.add(node)
s


# ## Saving

# In[85]:


os.chdir(direct)
doc.save('{0}-akk-pos.txt'.format(CORPUS))


# In[ ]:




