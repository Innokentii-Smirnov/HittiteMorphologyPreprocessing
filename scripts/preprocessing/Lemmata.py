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
doc = Document.load('{0}-determinatives.txt'.format(CORPUS))
len(doc)


# In[6]:


segments = doc.segments
len(segments)


# In[7]:


nodes = doc.wordforms
len(nodes)


# ## Analytics

# In[8]:


from library.iterable import group_by
by_lemma = group_by(lambda node: node.lemma, filter(lambda node: node.lemma is not None and node.segment.lang == 'sux', nodes))
len(by_lemma)


# In[9]:


no_boundary = list(filter(lambda lemma: '=' not in lemma, by_lemma))
len(no_boundary)


# ## Annotation tables

# ### Sumerograms

# #### Tables

# In[11]:


import pandas as pd
tables_folder = path.join(hm, 'Annotation tables')
assert path.exists(tables_folder)
os.chdir(tables_folder)


# In[12]:


colnamefunc = lambda x: x.replace(' ', '_').replace('.','')


# In[13]:


sumer_main = pd.read_excel("Sumerogramme.ods", dtype=str, engine='odf')
sumer_main.rename(colnamefunc, axis='columns', inplace=True)
sumer_main.rename({'Deriv': 'Derivation',
                   'engl_Bedeutung': 'englische_Bedeutung',
                   'Anm': 'Anmerkung'}, axis='columns', inplace=True)
sumer_main.head()


# In[14]:


sumer_dn = pd.read_excel("Sumerogramme_DN.ods", dtype=str, engine='odf')
sumer_dn.rename(colnamefunc, axis='columns', inplace=True)
sumer_dn.rename({'Anm': 'Anmerkung'}, axis='columns', inplace=True)
sumer_dn.head()


# In[15]:


sumer_gn = pd.read_excel("Sumerogramme_GN.ods", dtype=str, engine='odf')
sumer_gn.rename(colnamefunc, axis='columns', inplace=True)
sumer_gn.rename({'konkrete_Bedeutng': 'konkrete_Bedeutung'}, axis='columns', inplace=True)
sumer_gn.head()


# In[16]:


sumer_akk_compl = pd.read_excel("Sumerogramme_AKK_KOMPL.ods", dtype=str, engine='odf')
sumer_akk_compl.rename(colnamefunc, axis='columns', inplace=True)
sumer_akk_compl.rename({'Archilem': 'Archilemma',
                        'Det':'Determinativ',
                        'Sumerogramm-AKK': 'Stammform',
                        'Unnamed:_5': 'Determinativ1',
                        'Stkl': 'Stammklasse',
                        'Englisch': 'englische_Bedeutung'}, axis='columns', inplace=True)
sumer_akk_compl.head()


# In[17]:


for x in [sumer_main, sumer_dn, sumer_gn, sumer_akk_compl]:
    print(x.shape)


# In[18]:


sumer = pd.concat([sumer_main, sumer_dn, sumer_gn, sumer_akk_compl])
print(sumer.shape)
sumer.head()


# In[19]:


delta = 8272
for i in range(8320, 8330):
    subscript = chr(i)
    digit = chr(i - delta)
    col = 'Stammform'
    sumer[col] = sumer[col].str.replace(subscript, digit)
    print(subscript, digit)


# In[20]:


for col in sumer.columns:
    print(col, sumer[col].dtype)


# In[21]:


for col in sumer.columns:
    idx = sumer[col].notna()
    sumer.loc[idx, col] = sumer[col][idx].astype(str).str.strip().str.normalize('NFKC')
sumer.head()


# #### Direct lookup

# In[22]:


lexicon = group_by(lambda entry: entry.Stammform, sumer.itertuples())
len(lexicon)


# In[23]:


import re
pat = re.compile(r'eine? ')

def get_gloss(entry):
    if pd.notna(entry.konkrete_Bedeutung):
        return entry.konkrete_Bedeutung.split(', ')[0]
    elif pd.notna(entry.generische_Bedeutung):
        return "({0})".format(pat.sub('', entry.generische_Bedeutung))
    else:
        return '<ERR>'


# In[24]:


in_lex = list(filter(lambda lemma: lemma in lexicon, no_boundary))
for word in in_lex:
    print('{0:20} {1}'.format(word, ', '.join(set(get_gloss(x) for x in lexicon[word]))))


# In[25]:


not_in_lex = list(filter(lambda lemma: lemma not in lexicon, no_boundary))
len(not_in_lex)


# ### Indirect lookup

# In[26]:


missing = list(filter(lambda lemma: lemma +'=' not in lexicon, not_in_lex))
len(missing)


# In[27]:


candidates = {lemma: list(filter(lambda key: str(key).startswith(lemma + '='), lexicon)) for lemma in missing}


# In[28]:


notfound = list(filter(lambda lemma: len(candidates[lemma]) == 0, missing))
len(notfound)


# In[29]:


def get_form(node):
    return node.form


# In[30]:


for lemma, keys in sorted(candidates.items()):
    if len(keys) > 0:
        print('{0:20} {1:80}'.format(
            lemma,
            ', '.join('{0} \u2018{1}\u2019'.format(key,' | '.join(get_gloss(entry) for entry in lexicon[key])) for key in keys),
            )
        )
        print('{0:20} {1:80}'.format(
            '',
            ', '.join(set('{0} \u2018{1}\u2019'.format(get_form(node), node.gloss) for node in by_lemma[lemma]))
            )
        )


# In[31]:


negexc = set()
posexc = dict()

for lemma in missing:
    for node in by_lemma[lemma]:
        selected_lemmata = set()
        for candidate in candidates[lemma]:
            for entry in lexicon[candidate]:
                if get_gloss(entry) == node.gloss and entry.Stammklasse == node.misc['Class']:
                    selected_lemmata.add(entry)
        if len(selected_lemmata) == 0:
            negexc.add((get_form(node), node.misc['Class'], node.lemma, node.xpos, '\u2018{0}\u2019'.format(node.gloss)))
        else:
            if len(selected_lemmata) > 1:
                posexc[(get_form(node), node.misc['Class'], node.lemma, node.xpos, '\u2018{0}\u2019'.format(node.gloss))] = selected_lemmata
                sel = max(selected_lemmata, key=lambda entry: len(by_lemma[entry.Stammform]) if entry.Stammform in by_lemma else 0)
                #print(sel.Stammform)
            else:
                sel = next(iter(selected_lemmata))
            node.lemma = sel.Stammform

for (form, sc, lemma, xpos, gloss), values in posexc.items():
    print("{0:10} {1:15} {2:20} {3:10} {4}".format(
      form,
      sc,
      lemma +' '+ gloss,
      xpos,
      '; '.join('{0} {1} [{2}]'.format(entry.Stammform, str(len(by_lemma.get(entry.Stammform, []))), entry.Stammklasse)  for entry in values)
    ))

#' ' + str(len(by_lemma.get(value, []))) + ' ' + '; '.join(set(get_form(x) for x in by_lemma.get(value, []))) for value in values)))


# In[32]:


for form, sc, lemma, xpos, gloss in sorted([str(x) for x in t] for t in negexc):
    print("{0:25} {1:15} {2:20} {3:10}".format(
      form,
      sc,
      lemma +' '+ gloss,
      xpos))


# In[33]:


present = list(filter(lambda lemma: lemma +'=' in lexicon, not_in_lex))
len(present)


# In[34]:


candidates2 = {lemma: list(filter(lambda key: str(key).startswith(lemma + '='), lexicon)) for lemma in present}


# In[35]:


for lemma, keys in sorted(candidates2.items()):
    if len(keys) > 0:
        print('{0:20} {1:80}'.format(
            lemma,
            ', '.join('{0} \u2018{1}\u2019'.format(key,' | '.join(get_gloss(entry) for entry in lexicon[key])) for key in keys),
            )
        )
        print('{0:20} {1:80}'.format(
            '',
            ', '.join(set('{0} \u2018{1}\u2019'.format(get_form(node), node.gloss) for node in by_lemma[lemma]))
            )
        )


# In[36]:


negexc = set()
posexc = dict()

for lemma in present:
    for node in by_lemma[lemma]:
        selected_lemmata = set()
        for candidate in candidates2[lemma]:
            for entry in lexicon[candidate]:
                if get_gloss(entry) == node.gloss and entry.Stammklasse == node.misc['Class']:
                    selected_lemmata.add(entry)
        if len(selected_lemmata) == 0:
            negexc.add(node)
        else:
            if len(selected_lemmata) > 1:
                posexc[(get_form(node), node.misc['Class'], node.lemma, node.xpos, '\u2018{0}\u2019'.format(node.gloss))] = selected_lemmata
                sel = max(selected_lemmata, key=lambda entry: len(by_lemma[entry.Stammform]) if entry.Stammform in by_lemma else 0)
                #print(sel.Stammform)
            else:
                sel = next(iter(selected_lemmata))
            node.lemma = sel.Stammform

for (form, sc, lemma, xpos, gloss), values in posexc.items():
    print("{0:15} {1:10} {2:30} {3:15} {4}".format(
      form,
      sc,
      lemma +' '+ gloss,
      xpos,
      '; '.join('{0} {1} [{2}]'.format(entry.Stammform, str(len(by_lemma.get(entry.Stammform, []))), entry.Stammklasse)  for entry in values)
    ))


# In[37]:


len(negexc)


# In[38]:


left = group_by(lambda node: (node.lemma, node.gloss, node.misc['Class'], node.misc['Det']), negexc)
print(len(left))
for x in left:
    print(x)


# In[39]:


def format_class(sc: str):
    return '[{0}]'.format(sc)

def format_gloss(gloss: str):
    return '\u2018{0}\u2019'.format(gloss)


# #### By gloss only

# In[40]:


from collections import defaultdict
selected1 = defaultdict(set)
for (lemma, gloss, sc, det) in left:
    for candidate in candidates2[lemma]:
        for entry in lexicon[candidate]:
            if get_gloss(entry) == gloss:
                selected1[(lemma, gloss, sc, det)].add(entry)

for (lemma, gloss, sc, det), values in selected1.items():
    print("{0:17} {1:11} {2:25} {3}".format(
      lemma,
      format_class(sc),
      format_gloss(gloss),
      '; '.join('{0} {1} [{2}] {3} {4}'.format(entry.Stammform,
                                           str(len(by_lemma.get(entry.Stammform, []))),
                                           entry.Stammklasse,
                                           format_gloss(get_gloss(entry)),
                                           str(entry.Determinativ)) for entry in values)
    ))


# In[41]:


for key, values in selected1.items():
    for node in left[key]:
        value = next(iter(values))
        print(value.Stammform)
        node.lemma = value.Stammform


# #### By stem class only

# In[42]:


from collections import defaultdict
selected2 = defaultdict(set)
for (lemma, gloss, sc, det) in left:
    for candidate in candidates2[lemma]:
        for entry in lexicon[candidate]:
            if entry.Stammklasse == sc:
                selected2[(lemma, gloss, sc, det)].add(entry)

for (lemma, gloss, sc, det), values in selected2.items():
    print("{0:17} {1:11} {2:25} {3}".format(
      lemma,
      format_class(sc),
      format_gloss(gloss),
      '; '.join('{0} {1} [{2}] {3} {4}'.format(entry.Stammform,
                                           str(len(by_lemma.get(entry.Stammform, []))),
                                           entry.Stammklasse,
                                           format_gloss(get_gloss(entry)),
                                           str(entry.Determinativ)) for entry in values)
    ))


# In[43]:


for key, values in selected2.items():
    for node in left[key]:
        value = next(iter(values))
        print(value.Stammform)
        node.lemma = value.Stammform


# #### By lemma only

# In[44]:


from collections import defaultdict
selected3 = defaultdict(set)
for (lemma, gloss, sc, det) in set(left).difference(set(selected1)|set(selected2)):
    for candidate in candidates2[lemma]:
        for entry in lexicon[candidate]:
            selected3[(lemma, gloss, sc, det)].add(entry)

for (lemma, gloss, sc, det), values in selected3.items():
    print("{0:10} {1:15} {2:15} {3:35} {4}".format(
      lemma,
      format_class(sc),
      str(det),
      format_gloss(gloss),
      '; '.join('{0} {1} [{2}] {3} {4}'.format(entry.Stammform,
                                           str(len(by_lemma.get(entry.Stammform, []))),
                                           entry.Stammklasse,
                                           format_gloss(get_gloss(entry)),
                                           str(entry.Determinativ)) for entry in values)
    ))


# In[45]:


for key, values in selected3.items():
    if key[0] == 'NÍG.LÁM':
        index = 1
    elif key[0] == 'ŠU.GI':
        index = 0
    else:
        continue
    for node in left[key]:
        valuelist = list(values)
        value = valuelist[index]
        print(node.lemma, node.xpos)
        print(value.Stammform)
        node.lemma = value.Stammform


# ## Final analytics

# In[46]:


from library.iterable import group_by
by_lemma = group_by(lambda node: node.lemma, filter(lambda node: node.lemma is not None and node.segment.lang == 'sux', nodes))
len(by_lemma)


# In[47]:


no_boundary = list(filter(lambda lemma: '=' not in lemma, by_lemma))
len(no_boundary)


# ## Saving

# In[48]:


os.chdir(direct)
doc.save('{0}-lemmata.txt'.format(CORPUS))
