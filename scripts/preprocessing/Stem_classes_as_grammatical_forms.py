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
doc = Document.load('{0}-decomponed-tags.txt'.format(CORPUS))
len(doc)


# In[6]:


segments = doc.segments
len(segments)


# In[7]:


nodes = doc.wordforms
len(nodes)


# In[8]:


sum(1 for node in nodes if node.upos is None)


# ## Main

# ### Extracting grammatical forms

# In[9]:


no_xpos = [node for node in nodes if node.upos is None and node.xpos is None]


# In[10]:


gfs = set(node.misc['Class'] for node in no_xpos)
len(gfs)


# In[11]:


from library.iterable import group_by, modify_values
from functools import partial
bygf = group_by(lambda node: node.misc['Class'], no_xpos)
len(bygf)


# In[12]:


from library.corrector import Corrector
from hit_morph.parsing.gramm_forms import preprocess_gramm_form
corr = Corrector(path.join(HM, 'Corrections/Grammatical forms.txt'))
prepr_gfs = sorted(set(str(preprocess_gramm_form(corr(gf))) for gf in gfs))
len(prepr_gfs)


# In[13]:


by_prepr_gf = group_by(lambda node: preprocess_gramm_form(corr(node.misc['Class'])), no_xpos)
len(by_prepr_gf)


# ### Definitions

# In[14]:


def get_form(node) -> str:
    return node.form


# In[15]:


from collections.abc import Iterable

def print_gfs_from(gfs: Iterable[str], bygf: dict[str, list]):
    for gf in sorted(gfs):
        print('{0:25} {1:10} {2}'.format(gf, '({0})'.format(len(bygf[gf])),
                                         ', '.join(list(set(str(get_form(node)) for node in bygf[gf]))[:5])))


# In[16]:


from functools import partial
print_gfs = partial(print_gfs_from, bygf=bygf)
print_prepr_gfs = partial(print_gfs_from, bygf=by_prepr_gf)


# In[17]:


def is_class(gf: str):
    return all(x.isdigit() for x in gf.split('.'))


# ### Lexical information

# In[18]:


from library.iterable import group_by
grouped = group_by(lambda node: node.upos, nodes)
for key, values in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
    print("{0:15} {1:10}".format(str(key), str(len(values))))


# In[19]:


grouped['INT'][0].form


# In[20]:


by_class = group_by(lambda node: (node.misc['Class'], node.xpos), grouped[None])


# In[21]:


for (cl, xpos), values in sorted(by_class.items(), key=lambda x: len(x[1]), reverse=True):
    #if not all(x.isdigit() for x in cl.split('.')):
        #if xpos is None:
    print("{0:25} {1:10} {2:10}".format(str(cl), str(xpos) or '', str(len(values))))


# ## Corrections for numerals

# In[22]:


print_gfs(gf for gf in gfs if gf and 'QUANcar' in gf)


# ### First

# In[23]:


to_correct = 'QUANcar.ACC.SG.C QUANcar.NOM/ACC.SG.N'


# In[24]:


variants  = ['QUANcar.ACC.SG.C','QUANcar.NOM.SG.N', 'QUANcar.ACC.SG.N']


# In[25]:


from hit_morph.struct.clitic_complex import CliticComplex
mod = list()

for clitic_complex in doc.clitic_complexes:
    if clitic_complex.morpholex.stem_class == to_correct:
        segment = clitic_complex.morpholex.segment
        segment.analyses.remove(clitic_complex)
        for variant in variants:
            segment.analyses.append(CliticComplex.from_string(repr(clitic_complex).replace(to_correct, variant)))
        mod.append(segment)


# ### Second

# In[26]:


to_correct = 'QUANcar.D/L'


# In[27]:


variants  = {0: 'QUANcar.D/L.PL'}


# In[28]:


from hit_morph.struct.clitic_complex import CliticComplex
mod = list()

for clitic_complex in doc.clitic_complexes:
    if clitic_complex.morpholex.stem_class == to_correct:
        segment = clitic_complex.morpholex.segment
        segment.analyses.remove(clitic_complex)
        for variant in variants.values():
            segment.analyses.append(CliticComplex.from_string(repr(clitic_complex).replace(to_correct, variant)))
        mod.append(segment)


# ### Third

# In[29]:


to_correct = 'QUANcar.ALL QUANcar.INS'


# In[30]:


variants  = {0: 'QUANcar.ALL',
             1: 'QUANcar.INS'}


# In[31]:


from hit_morph.struct.clitic_complex import CliticComplex
mod = list()

for clitic_complex in doc.clitic_complexes:
    if clitic_complex.morpholex.stem_class == to_correct:
        segment = clitic_complex.morpholex.segment
        segment.analyses.remove(clitic_complex)
        for variant in variants.values():
            segment.analyses.append(CliticComplex.from_string(repr(clitic_complex).replace(to_correct, variant)))
        mod.append(segment)

# ### Fourth

# In[32]:


to_correct = 'QUANcar C'


# In[33]:


variants  = {0: 'QUANcar.ACC.SG.C'}


# In[34]:


from hit_morph.struct.clitic_complex import CliticComplex
mod = list()

for clitic_complex in doc.clitic_complexes:
    if clitic_complex.morpholex.stem_class == to_correct:
        segment = clitic_complex.morpholex.segment
        segment.analyses.remove(clitic_complex)
        for variant in variants.values():
            segment.analyses.append(CliticComplex.from_string(repr(clitic_complex).replace(to_correct, variant)))
        mod.append(segment)

# ### Fifth

# In[35]:


to_correct = 'QUANcar.GEN'


# In[36]:


variants  = {0: 'QUANcar.GEN.PL'}


# In[37]:


from hit_morph.struct.clitic_complex import CliticComplex
mod = list()

for clitic_complex in doc.clitic_complexes:
    if clitic_complex.morpholex.stem_class == to_correct:
        segment = clitic_complex.morpholex.segment
        segment.analyses.remove(clitic_complex)
        for variant in variants.values():
            segment.analyses.append(CliticComplex.from_string(repr(clitic_complex).replace(to_correct, variant)))
        mod.append(segment)

# ### Final

# In[38]:


for segment in doc.segments:
    segment.mark_morphs()
no_xpos = [node for node in doc.wordforms if node.upos is None and node.xpos is None]
gfs = set(node.stem_class if node.xpos is None else node.xpos for node in no_xpos)
bygf = group_by(lambda node: node.misc['Class'] if node.xpos is None else node.xpos, no_xpos)
print_gfs = partial(print_gfs_from, bygf=bygf)
print(len(gfs))
print_gfs(gf for gf in gfs if gf and 'QUANcar' in gf)


# ## Initial grammatical forms

# In[39]:


print_gfs(gf for gf in gfs if gf is not None and not is_class(gf))


# ## Grammatical forms

# In[40]:


from library.corrector import Corrector
from importlib import reload
import gen_morph.gramm_forms.decomponer
reload(gen_morph.gramm_forms.decomponer)
import gen_morph.gramm_systems.gramm_system
reload(gen_morph.gramm_systems.gramm_system)
from gen_morph.gramm_forms.decomponer import Decomponer
from gen_morph.gramm_systems.gramm_system import GrammaticalSystem
import hit_morph.parsing.gramm_forms
reload(hit_morph.parsing.gramm_forms)
from hit_morph.parsing.gramm_forms import preprocess_gramm_form
from gen_morph.exceptions import CannotParseGrammForm


# In[42]:


corr = Corrector(path.join(HM, 'Corrections/Classes.txt'))
gs = GrammaticalSystem.from_file(path.join(hm, 'Tag structure/Classes system.txt'))
dec = Decomponer.from_file(path.join(hm, 'Tag structure/Classes decomponer.txt'), gs.properties)
errs = set()
for gf in gfs:
    if gf is not None and not is_class(gf):
        preprocessed = preprocess_gramm_form(corr(gf))
        try:
            dec('any', preprocessed)
        except CannotParseGrammForm:
            errs.add((gf, preprocessed))
len(errs)


# In[43]:


for gf, y in sorted(errs):
    print("{0:15} {1:15} {2:10} {3:30}".format(gf, y if gf!=y else '=', str(len(bygf[gf])),
                                     ', '.join(list(set('{0} {1} \u2018{2}\u2019'.format(get_form(node),
                                                                                     node.lemma if node.lemma != node.form else '',
                                                                                     node.gloss)
                                     for node in bygf[gf]))[:5])))


# In[44]:


set((get_form(node), node.xpos, node.gloss) for node in nodes if node.gloss and 'zusammen' in node.gloss)


# ## Corrections

# ### First

# In[45]:


to_correct = 'QUAN:ACC'
range = bygf.get(to_correct, [])
range


# In[46]:


for elem in range:
    elem.stem_class = 'QUANcar.NOM.PL.C'


# In[47]:


range


# ## Empty class

# In[48]:


byexp = group_by(lambda node: (node.form, node.lemma, node.gloss), by_class[(None, None)])
len(byexp)


# In[49]:


for key, values in byexp.items():
    print(key, len(values))


# ### Modifications

# In[50]:


for node in nodes:
    if node.upos is None:
        if node.gloss and node.gloss.startswith('CLFcas'):
            node.upos = 'PREP'
            print(node)


# ## Corrections

# In[51]:


curr = 'É.ŠÀ', 'É.ŠÀ=', 'Innengemach'
for node in doc.wordforms:
    if (node.form, node.lemma, node.gloss) == curr and node.xpos is None and node.stem_class is None:
        print(node.segment)
        node.stem_class = 'D/L.SG'


# In[52]:


curr = 'erama', 'erama', '(Name oder Bezeichnung eines Pferds)'
for node in doc.wordforms:
    if (node.form, node.lemma, node.gloss) == curr and node.xpos is None and node.stem_class is None:
        node.stem_class = 'D/L.SG'
        print(node.segment)


# In[53]:


curr = 'IGIzi', 'IGI-zi', 'sehen'
for node in doc.wordforms:
    if (node.form, node.lemma, node.gloss) == curr and node.xpos is None and node.stem_class is None:
        node.stem_class = '3PL.PRS'
        print(node.segment)


# In[54]:


curr = '%-%-la', None, None
for node in doc.wordforms:
    if (node.form, node.lemma, node.gloss) == curr and node.xpos is None and node.stem_class is None:
        node.stem_class = 'QUANcar.NOM.PL.C'
        print(node.segment)


# In[55]:


curr = '%', None, None
for node in doc.wordforms:
    if (node.form, node.lemma, node.gloss) == curr and node.xpos is None and node.stem_class is None:
        node.stem_class = 'QUANcar'
        print(node.segment)


# ## Modifications

# In[56]:


def get_xpos(pos: str, gf: str):
    if pos == gf:
        return None
    elif pos + '.' in gf:
        return gf.replace(pos + '.', '')
    elif '.' + pos in gf:
        return gf.replace('.' + pos, '')
    else:
        return gf.replace(pos, '')


# In[57]:


modified = set()

for node in doc.wordforms:
    if node.upos is None:
        if node.xpos is None:
            if node.stem_class is not None and not is_class(node.stem_class):
                node.xpos = node.stem_class
                modified.add(node.segment.sentence)
        if node.xpos is not None:
            gf = preprocess_gramm_form(corr(node.xpos))
            try:
                decomponed, struct = dec('any', gf)
            except CannotParseGrammForm:
                print(node)
                continue
            if 'pos' in decomponed:
                pos = decomponed['pos']
                node.upos = pos
                del decomponed['pos']
                node.xpos = get_xpos(pos, gf)
            elif struct is not None:
                node.upos = struct.upper()
                node.xpos = gf
            node.feats = decomponed
            modified.add(node.segment.sentence)


# In[58]:


mod = sorted(modified, key = lambda sent: sent.metadata.text_name)


# In[59]:


len(mod)


# In[60]:


mod[896]


# ## Final analytics

# In[61]:


nodes = doc.wordforms


# In[62]:


set(node.stem_class for node in nodes if node.upos is None)


# In[63]:


set((node.stem_class, node.upos) for node in nodes if node.xpos=='HATT')


# In[64]:


from library.iterable import group_by
grouped = group_by(lambda node: node.upos, nodes)
for key, values in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
    print("{0:15} {1:10}".format(str(key), str(len(values))))


# In[65]:


by_class = group_by(lambda node: (node.stem_class, node.xpos), grouped[None])


# In[66]:


for (cl, xpos), values in sorted(by_class.items(), key=lambda x: len(x[1]), reverse=True):
    #if not all(x.isdigit() for x in cl.split('.')):
        #if xpos is None:
    print("{0:25} {1:10} {2:10}".format(cl or '', xpos or '', str(len(values))))


# ## Saving

# In[67]:


doc.save('{0}-classes-as-grammforms.txt'.format(CORPUS))


# In[ ]:




