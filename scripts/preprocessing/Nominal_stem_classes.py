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
doc = Document.load('{0}-classes-as-grammforms.txt'.format(CORPUS))
len(doc)


# In[6]:


segments = doc.segments
len(segments)


# In[7]:


nodes = doc.wordforms
len(nodes)


# In[8]:


sum(1 for node in nodes if node.upos is None)


# In[9]:


print(doc[9].metadata)


# ## Main

# ### Startup

# In[10]:


def get_form(node) -> str:
    return node.form


# In[11]:


from library.iterable import count
count(lambda node: node.upos is None, nodes)


# In[12]:


set((get_form(node), node.xpos, node.misc['Class']) for node in nodes if node.upos is None)


# In[13]:


from library.iterable import count
count(lambda node: node.upos == 'NOMINAL', nodes)


# ### Extracting grammatical forms

# In[14]:


nominals = [node for node in nodes if node.upos == 'NOMINAL' and node.stem_class is not None]


# In[15]:


gfs = set(node.misc['Class'] for node in nominals)
len(gfs)


# In[16]:


from library.iterable import group_by, modify_values
from functools import partial
bygf = group_by(lambda node: node.misc['Class'], nominals)
len(bygf)


# In[17]:


from library.corrector import Corrector
from hit_morph.parsing.gramm_forms import preprocess_gramm_form
#corr = Corrector(path.join(HM, 'Corrections/Grammatical forms.txt'))
#prepr_gfs = sorted(set(preprocess_gramm_form(corr(gf)) for gf in gfs))
#len(prepr_gfs)


# In[18]:


#by_prepr_gf = group_by(lambda node: preprocess_gramm_form(corr(node.misc['Class'])), no_xpos)
#len(by_prepr_gf)


# ### Definitions

# In[19]:


from collections.abc import Iterable
from hit_morph.struct.morpholex import Morpholex
Node = Morpholex

def print_gfs_from(gfs: Iterable[str], bygf: dict[str, list[Node]]):
    for gf in sorted(gfs):
        print('{0:25} {1:10} {2}'.format(gf, '({0})'.format(len(bygf[gf])),
                                         ', '.join(list(set(str(get_form(node)) for node in bygf[gf]))[:5])))


# In[20]:


from functools import partial
print_gfs = partial(print_gfs_from, bygf=bygf)
#print_prepr_gfs = partial(print_gfs_from, bygf=by_prepr_gf)


# In[21]:


def is_class(gf: str):
    return all(x.isdigit() for x in gf.split('.'))


# In[22]:


print_gfs(gfs)


# In[23]:


bygf['QUANcar'][0]


# ## Corrections

# In[24]:


class writer:
    @classmethod
    def process_tree(cls, x):
        print(repr(x))

for node in nodes:
    node.root = node.segment.sentence
    node.feats = dict()


# ### šauar

# In[25]:


list((node.upos, node.xpos, node.lemma) for node in nodes if get_form(node) == 'šauar')


# In[26]:


#for root in list(node.root for node in bygf.get('15.1', [])):
#    writer.process_tree(root)


# In[27]:


for node in bygf.get('I.10.3', []):
    print(node.segment)
    #writer.process_tree(node.root)
    #node.lemma = bygf['15.1'][0].lemma
    #node.misc['Class'] = bygf['15.1'][0].misc['Class']
    #node.gloss = bygf['15.1'][0].gloss
    #writer.process_tree(node.root)


# ### zeanta

# In[28]:


for node in bygf.get('III.2', []):
    #writer.process_tree(node.root)
    node.upos = 'VERB'
    node.xpos = 'PTCP.{0}'.format(node.xpos)
    node.feats['verbform'] = 'PTCP'
    #writer.process_tree(node.root)


# ### ištamašuarat

# In[29]:


for node in bygf.get('I.1.1', []):
    #writer.process_tree(node.root)
    node.upos = 'VERB'
    node.xpos = 'VBN.{0}'.format(node.xpos)
    node.feats['verbform'] = 'VBN'
    #writer.process_tree(node.root)


# ### warpuar

# In[30]:


for node in bygf.get('I.1.2', []):
    #writer.process_tree(node.root)
    node.upos = 'VERB'
    node.xpos = 'VBN.{0}'.format(node.xpos)
    node.feats['verbform'] = 'VBN'
    #writer.process_tree(node.root)


# ## Stem classes

# In[31]:


from library.iterable import group_by
nominals = [node for node in nodes if node.upos == 'NOMINAL' and node.stem_class is not None]
grouped = group_by(lambda node: node.misc['Class'], nominals)


# In[32]:


stem_classes = sorted(set(node.misc['Class'] for node in nominals))


# In[33]:


print(stem_classes)


# In[34]:


from importlib import reload
import hit_morph.enumerations
reload(hit_morph.enumerations)
import hit_morph.parsing.stem_classes
reload(hit_morph.parsing.stem_classes)
from hit_morph.parsing.stem_classes import parse_stem_class
from gen_morph.exceptions import CannotParseStemClass


# In[35]:


correct = []
errs = []
for stem_class in stem_classes:
    try:
        lang, pos, feats = parse_stem_class(stem_class)
        #if pos.name == 'VERB' and 'verbform' not in feats:
        #    feats['verbform'] = 'VBN'
        result = lang, pos, feats
        correct.append((stem_class, result))
    except CannotParseStemClass:
        errs.append(stem_class)
        print(stem_class)


# In[36]:


print_gfs(errs)


# In[37]:


set((get_form(node), node.upos, node.xpos, node.gloss) for node in bygf['30.12'])


# In[38]:


from collections import Counter
Counter((node.upos, node.xpos, node.gloss) for node in nodes if node.form == 'ḫepat')


# In[39]:


for node in bygf.get('35.6.1', []):
    print(node.form, node.lemma, node.upos, node.xpos, node.gloss, node.misc['Class'], sep='\t')


# In[40]:


ok = {'NOUN', 'ADJ', 'DN', 'GN', 'PNm', 'PNf', 'DEM', 'INDF', 'QUAN'}


# In[41]:


for sc, (lang, pos, feats) in sorted(correct, key=lambda sc: tuple(int(x) if x.isdigit() else 0 for x in sc[0].split('.'))):
    #if pos.name not in ok:
    print('{0:15} {1:6} {2:6} {3:15} {4:10} {5}'.format(sc, pos.name, lang.name, '.'.join(feats.values()), '({0})'.format(len(grouped[sc])),
                                        ', '.join(list(set('{0} ({1}) \u2018{2}\u2019 {3}'.format(get_form(node),
                                                                                                  node.lemma,
                                                                                                  node.gloss,
                                                                                                  node.xpos) for node in bygf[sc]))[:5])))


# In[42]:


set((node.upos, node.xpos) for node in nodes if node.lemma == 'aši')


# In[43]:


set((node.upos, node.xpos) for node in nodes if node.lemma == 'kuišša')


# In[44]:


set((node.upos, node.xpos) for node in nodes if node.lemma == 'ḫumant-')


# ## Adjectival sumerograms

# ### 29.1.1

# In[45]:


set(node.gloss for node in grouped['29.1.1'] if node.gloss.islower())


# In[46]:


for node in grouped['29.1.1']:
    if node.gloss.islower():
        node.upos = 'ADJ'


# In[47]:


sum(1 for node in grouped['29.1.1'] if node.upos == 'ADJ')


# In[48]:


set(node.gloss for node in grouped['29.1.1'] if not node.gloss.islower())


# In[49]:


s = set()
for node in grouped['29.1.1']:
    if not node.gloss.islower():
        if node.gloss.startswith('aus Rohrgeflecht'):
            node.upos = 'ADJ'
            s.add(node)
        else:
            node.upos = 'NOUN'
s


# ### 29.1.2

# In[50]:


Counter(node.gloss for node in grouped['29.1.2'] if node.gloss.islower())


# In[51]:


for node in grouped['29.1.2']:
    if node.gloss.islower():
        node.upos = 'ADJ'


# In[52]:


writer.process_tree(next(node.root for node in grouped['29.1.2'] if node.upos == 'ADJ'))


# In[53]:


sum(1 for node in grouped['29.1.2'] if node.upos == 'ADJ')


# In[54]:


Counter(node.gloss for node in grouped['29.1.2'] if not node.gloss.islower())


# ## Modifications

# In[55]:


from udapi.core.root import Root
modified = list[Root]()
modified_xpos = list[Root]()

for sc, (lang, pos, feats) in correct:
    nodes = grouped[sc]
    for node in nodes:
        if node.upos == 'NOMINAL':
            node.upos = pos.name
            if 'prontype' in feats:
                #assert 'prontype' not in node.feats
                #node.feats['prontype'] = feats['prontype']
                assert node.xpos is not None
                node.xpos = '{0}.{1}'.format(feats['prontype'], node.xpos)
                modified_xpos.append(node.root)
            modified.append(node.root)


# In[56]:


print(len(modified_xpos))
for root in sorted(modified_xpos, key=id):
    writer.process_tree(root)


# In[57]:


from random import choices
print(len(modified))
for root in choices(list(modified), k=5):
    writer.process_tree(root)
    print()
    print()


# ## Other

# In[58]:


Counter((node.gloss, node.misc['Class']) for node in nominals if node.upos == 'NOUN' and node.gloss.islower())


# In[59]:


for node in nominals:
    if node.upos == 'NOUN' and node.gloss.islower():
        node.upos = 'ADJ'


# In[61]:


next(node for node in grouped['28.2.1.1'] if node.upos == 'ADJ').segment.sentence


# In[62]:


sum(1 for node in grouped['1.1.1'] if node.upos == 'ADJ')


# ## Errors

# In[63]:


print_gfs(errs)


# ### Other

# #### D/L.SG

# In[64]:


for node in bygf.get('D/L.SG', []):
    print(node)


# In[65]:


for node in bygf.get('D/L.SG', []):
    if node.gloss == 'Innengemach':
        node.upos = 'NOUN'
    else:
        node.upos = 'ADJ'
    writer.process_tree(node.root)
    print('\n\n***\n\n')


# #### GEN.SG(ABBR)

# In[66]:


for node in bygf.get('GEN.SG(ABBR)', []):
    writer.process_tree(node.root)
    node.upos = 'NOUN'
    print()
    print(node)


# #### HURR.GEN

# In[67]:


for node in bygf.get('HURR.GEN', []):
    writer.process_tree(node.root)
    node.upos = 'NOUN'
    print()
    print(node)


# #### NOM.SG(UNM)

# In[68]:


for node in bygf.get('NOM.SG(UNM), ACC.SG(UNM), NOM.PL(UNM), ACC.PL(UNM), GEN.SG(UNM), GEN.PL(UNM), D/L.SG(UNM), D/L.PL(UNM), ALL(UNM), ABL(UNM), INS(UNM), VOC.SG(UNM), VOC.PL(UNM)', []):
    writer.process_tree(node.root)
    node.upos = 'NOUN'
    print()
    print(node)


# #### ?

# In[69]:


for node in bygf.get('?', []):
    writer.process_tree(node.root)
    node.upos = 'NOUN'
    print()
    print(node)


# #### QUANdist

# In[70]:


for node in bygf.get('QUANdist', []):
    writer.process_tree(node.root)
    node.upos = 'QUAN'
    node.xpos = '{0}.{1}'.format('dist', node.xpos)
    node.feats['quantype'] = 'dist'
    print()
    print(node)


# #### QUANcar

# In[71]:


set(bygf['QUANcar'])


# In[72]:


from random import choice
node = choice(bygf['QUANcar'])
node.label


# In[74]:


node.root


# In[75]:


root = choice(bygf['QUANcar']).root
writer.process_tree(root)
for node in bygf['QUANcar']:
    node.upos = 'QUAN'
    node.xpos = '{0}.{1}'.format('car', node.xpos)
    #node.feats['quantype'] = 'car'
print()
writer.process_tree(root)


# ### No stem class

# In[76]:


for form, gloss in sorted(set((get_form(node), node.gloss or '') for node in doc.wordforms if node.upos =='NOMINAL' and node.stem_class is None)):
    if not gloss.islower():
        print('{0:25} \u2018{1}\u2019'.format(form, gloss))


# In[ ]:


for form, gloss in sorted(set((get_form(node), node.gloss or '') for node in doc.wordforms if node.upos =='NOMINAL' and node.stem_class is None)):
    if gloss.islower():
        print('{0:25} \u2018{1}\u2019'.format(form, gloss))


# ## Printing

# In[ ]:


stem_class = '28.2.1.2'
print(len(grouped[stem_class]))


# In[ ]:


groups = group_by(lambda node: node.xpos, grouped[stem_class])
for key, values in groups.items():
    print('{0:10} {1:7} {2:25}'.format(key, str(len(values)), ', '.join(set(node.form if node.form != '_' else
                                                                            "[{0}]".format(node.multiword_token.form)
                                                                            for node in values))))


# In[ ]:


for node in groups['ACC.SG.C']: #grouped[stem_class]:
    writer.process_tree(node.root)
    print()


# In[ ]:


correct[5]


# ## Final analytics

# In[ ]:


nominals = [node for node in doc.wordforms if node.upos =='NOMINAL']
len(nominals)


# In[ ]:


groups = group_by(lambda node: node.misc["Class"], nominals)
for key, value in groups.items():
    print(key, len(value))


# ## No upos

# ### Analytics

# In[ ]:


noupos = [node for node in doc.wordforms if node.upos is None]
len(noupos)


# In[ ]:


groups = group_by(lambda node: (node.misc["Class"], node.xpos), noupos)
for key, value in groups.items():
    print(key, len(value), sep='\t\t')


# ### Hattic

# In[ ]:


set((node.gloss, node.gloss.islower()) for node in groups['30.11', 'HATT'])


# In[ ]:


modifications = set()

for node in groups['30.11', 'HATT']:
    if node.gloss.islower():
        node.upos = 'VERB'
    else:
        node.upos = 'NOUN'
    modifications.add((node.gloss, node.upos))

modifications


# ### Hurritic

# In[ ]:


Counter((get_form(node), node.gloss) for node in groups.get(('HURR', 'HURR'), []))


# In[ ]:


for node in groups.get(('HURR', 'HURR'), []):
    if node.gloss == '(Kultobjekt)':
        node.upos = 'NOUN'
    else:
        node.upos = 'X'


# In[ ]:


roots = list(node.root for node in groups.get(('HURR', 'HURR'), []))
len(roots)


# In[77]:


for root in roots:
    writer.process_tree(root)
    print()


# ### Other

# In[ ]:


noupos = [node for node in doc.wordforms if node.upos is None]
len(noupos)


# In[ ]:


grouped = group_by(lambda node: node.misc['Class'], noupos)


# In[ ]:


grouped[None]


# In[ ]:


del grouped[None]


# In[ ]:


stem_classes = sorted(grouped)


# In[ ]:


from importlib import reload
import hit_morph.enumerations
reload(hit_morph.enumerations)
import hit_morph.parsing.stem_classes
reload(hit_morph.parsing.stem_classes)
from hit_morph.parsing.stem_classes import parse_stem_class
from gen_morph.exceptions import CannotParseStemClass


# In[ ]:


correct = []
errs = []
for stem_class in stem_classes:
    try:
        lang, pos, feats = parse_stem_class(stem_class)
        #if pos.name == 'VERB' and 'verbform' not in feats:
        #    feats['verbform'] = 'VBN'
        result = lang, pos, feats
        correct.append((stem_class, result))
    except CannotParseStemClass:
        errs.append(stem_class)
        print(stem_class)


# In[ ]:


print_gfs_from(errs, grouped)


# In[ ]:


for sc, (lang, pos, feats) in sorted(correct, key=lambda sc: tuple(int(x) if x.isdigit() else 0 for x in sc[0].split('.'))):
    print('{0:15} {1:6} {2:4} {3:11} {4:10} {5}'.format(sc, pos.name, lang.name, str(feats), '({0})'.format(len(grouped[sc])),
                                        ', '.join(list(set('{0} ({1}) \u2018{2}\u2019 {3}'.format(get_form(node),
                                                                                                  node.lemma,
                                                                                                  node.gloss,
                                                                                                  node.xpos) for node in grouped[sc])))))


# ### Modifications

# In[ ]:


from udapi.core.root import Root
modified = list[Root]()

for sc, (lang, pos, feats) in correct:
    nodes = grouped[sc]
    for node in nodes:
        assert node.upos is None
        node.upos = pos.name
        modified.append(node.root)

len(modified)


# In[ ]:


from random import choices
print(len(modified))

for root in choices(list(modified), k=5):
    writer.process_tree(root)


# ### Restoring xpos

# In[ ]:


for node in grouped.get('38.2', []):
    print(node)
    print()
    node.xpos = 'GEN.SG'
    print(node.root)


# In[ ]:


roots = sorted(list(node.root for node in grouped['30.10.1']), key=id)
len(roots)


# In[ ]:


for root in roots:
    print(repr(root))
    print('\n***\n')


# In[ ]:


for node in grouped.get('30.10.1', []):
    print(node)


# ## Final analytics

# In[ ]:


nodes = doc.wordforms


# In[ ]:


noupos = [node for node in nodes if node.upos is None]
len(noupos)


# In[78]:


from collections import Counter
Counter(node.upos for node in nodes if node.xpos is None)


# ## Saving

# In[79]:


assert path.exists(direct)
os.chdir(direct)


# In[80]:


doc.save('{0}-stem-classes.txt'.format(CORPUS))


# ### Checking

# In[81]:


for stem_class, (lang, pos, feats) in correct:
    #if feats['Gender'] == 'Com,Neut':
    print('{0:15} {1:10} {2:10} {3:10}'.format(stem_class, lang.name, pos.name, str(feats)))


# In[82]:


from library.iterable import pi, compone


# In[83]:


set(map(str, compone(pi(1), pi(2))(correct)))


# In[ ]:




