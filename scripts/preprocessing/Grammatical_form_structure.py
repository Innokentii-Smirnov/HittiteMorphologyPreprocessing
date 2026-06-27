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
doc = Document.load('{0}-lemmata.txt'.format(CORPUS))
len(doc)


# In[6]:


segments = doc.segments
len(segments)


# In[7]:


nodes = doc.wordforms
len(nodes)


# ## Startup

# ### Extracting grammatical forms

# In[8]:


gfs = set(node.xpos for node in nodes if node.xpos is not None)
len(gfs)


# In[9]:


from library.iterable import group_by, modify_values
from functools import partial
bygf = group_by(lambda node: node.xpos, nodes)
len(bygf)


# In[10]:


from library.corrector import Corrector
from hit_morph.parsing.gramm_forms import preprocess_gramm_form
corr = Corrector(path.join(HM, 'Corrections/Grammatical forms.txt'))
prepr_gfs = sorted(set(preprocess_gramm_form(corr(gf)) for gf in gfs))
len(prepr_gfs)


# In[11]:


by_prepr_gf = group_by(lambda node: preprocess_gramm_form(corr(node.xpos)) if node.xpos is not None else node.xpos, nodes)
len(by_prepr_gf)


# ### Definitions

# In[12]:


from hit_morph.struct.morpholex import Morpholex

def get_form(node: Morpholex) -> str:
    return node.form


# In[13]:


from collections.abc import Iterable

def print_gfs_from(gfs: Iterable[str], bygf: dict[str, list[Morpholex]]):
    for gf in sorted(gfs):
        print('{0:25} {1:10} {2}'.format(gf, '({0})'.format(len(bygf.get(gf, []))),
                                         ', '.join(list(set(str(get_form(node)) for node in bygf.get(gf, [])))[:5])))


# In[14]:


from functools import partial
print_gfs = partial(print_gfs_from, bygf=bygf)
print_prepr_gfs = partial(print_gfs_from, bygf=by_prepr_gf)


# ### Initial grammatical forms

# In[15]:


print_gfs(gfs)


# ## Grammatical form structure

# ### Dative-locative

# In[16]:


set(
    (get_form(node),
     node.lemma)
    for node in by_prepr_gf.get('D/L', [])
)


# In[17]:


from hit_morph.struct.morpholex import Morpholex
modified = list[Morpholex]()
for node in by_prepr_gf.get('D/L', []):
    if node.form.endswith('aš'):
        node.xpos = 'D/L.PL'
    else:
        node.xpos = 'D/L.SG'
    modified.append(node)


# In[18]:


set((get_form(node), node.xpos) for node in modified)


# ### Corrections

# In[19]:


def correct_gramm_form(tag: str) -> str:
    feats = tag.split('.')
    if any(cas in feats for cas in {'ABL', 'ALL', 'D/L', 'GEN', 'VOC', 'INS'}):
        for gend in {'C', 'N'}:
            tag = tag.removesuffix('.' + gend)
    if any(cas in feats for cas in {'ABL', 'ALL', 'INS'}):
        for num in {'SG'}:
            tag = tag.removesuffix('.' + num)
    if any(cas in feats for cas in {'ABS'}):
        if feats[-1] not in {'SG', 'PL'}:
            tag += '.SG'
    tag = tag.replace('LUW/HITT.', 'HITT.')
    tag = tag.replace('HITT.', '')
    tag = tag.replace('INDoth', 'INDFoth')
    return tag


# In[20]:


print_prepr_gfs(['ALL', 'ALL.SG', 'ALL.SG.N', 'ALL.N', 'HURR.ABS.SG'])


# In[21]:


for gf in prepr_gfs:
    corr_gf = correct_gramm_form(gf)
    if corr_gf != gf:
        print('{0:25} {1:5} {2:6} {3:5} {4:25}'.format(gf,
                                                       '({0})'.format(len(by_prepr_gf[gf])),
                                                       '->',
                                                       corr_gf,
                                                       '({0})'.format(len(by_prepr_gf.get(corr_gf, [])))))


# ### Corrected

# In[22]:


by_corr_gf = group_by(lambda node: correct_gramm_form(preprocess_gramm_form(corr(node.xpos))) if node.xpos is not None else None, nodes)
len(by_corr_gf)


# In[23]:


corr_gfs = set(correct_gramm_form(preprocess_gramm_form(corr(node.xpos))) for node in nodes if node.xpos is not None)
len(corr_gfs)


# In[24]:


print_corr_gfs = partial(print_gfs_from, bygf=by_corr_gf)


# In[25]:


print_corr_gfs(corr_gfs)


# ### Grammatical forms

# In[26]:


from library.corrector import Corrector
from importlib import reload
import gen_morph.gramm_forms.decomponer
reload(gen_morph.gramm_forms.decomponer)
import gen_morph.gramm_systems.gramm_system
reload(gen_morph.gramm_systems.gramm_system)
from gen_morph.gramm_forms.decomponer import Decomponer
from gen_morph.gramm_systems.gramm_system import GrammaticalSystem
from hit_morph.parsing.gramm_forms import preprocess_gramm_form
from gen_morph.exceptions import CannotParseGrammForm


# In[27]:


corr = Corrector(path.join(HM, 'Corrections/Grammatical forms.txt'))
gs = GrammaticalSystem.from_file(path.join(hm, 'Tag structure/Grammatical system.txt'))
dec = Decomponer.from_file(path.join(hm, 'Tag structure/HFR-Decomponer.txt'), gs.properties)
errs = set()
for gf in set(node.xpos for node in nodes if node.xpos is not None):
    preprocessed = preprocess_gramm_form(corr(gf))
    corrected = correct_gramm_form(preprocessed)
    try:
        dec('any', corrected)
    except CannotParseGrammForm:
        errs.add((gf, corrected))
len(errs)


# In[28]:


for gf, y in sorted(errs):
    print("{0:30} {1:20} {2:10} {3:30}".format(gf, y if gf!=y else '=', str(len(bygf[gf])),
                                     ', '.join(list(set(str(get_form(node)) for node in bygf[gf]))[:5])))


# In[30]:


set(node for node in nodes if node.xpos == 'CNJ')


# In[31]:


bygf['NOM.SG.C'][0].segment


# In[32]:


set(get_form(node) for node in bygf['HURR'])


# ### Collective

# In[33]:


[node for node in nodes if node.xpos == 'ACC.COLL.C']


# ### Quantifiers

# In[34]:


print_gfs(gf for gf in gfs if 'QUAN' in gf)


# #### Not a number

# In[35]:


print(set(get_form(node) for node in by_corr_gf['QUANcar']))


# In[36]:


quantrees = list(set(node.segment.sentence for node in by_corr_gf['QUANcar'] if get_form(node) == 'nuarašta'))
len(quantrees)


# In[37]:


quantrees[:1]


# In[38]:


for node in by_corr_gf['QUANcar']:
    if get_form(node) == 'nuarašta':
        node.xpos = 'CONNn'
        print(node.segment.sentence)


# #### Normal

# In[39]:


by_corr_gf = group_by(lambda node: correct_gramm_form(preprocess_gramm_form(corr(node.xpos))) if node.xpos is not None else None, nodes)
len(by_corr_gf)


# In[40]:


print(set(get_form(node) for node in by_corr_gf['QUANcar']))


# In[41]:


quantrees = list(set(node.segment.sentence for node in by_corr_gf.get('QUANcar.NOM.SG', []) if get_form(node) == 'ŠU-ŠIiš'))
len(quantrees)


# In[42]:


for tree in quantrees:
     print(tree)


# ### Hittite and Luwian

# In[43]:


print_prepr_gfs([gf for gf in prepr_gfs if 'HITT' in gf])


# In[44]:


import re
hitt = set(get_form(node) for node in nodes if node.xpos and re.search(r'^(DN\.)?HITT', node.xpos))
print(sorted(hitt))
len(hitt)


# In[45]:


luw_hitt = set(get_form(node) for node in nodes if node.xpos and ('LUW||HITT' in node.xpos or 'LUW/HITT' in node.xpos))
print(sorted(luw_hitt))
len(luw_hitt)


# In[46]:


luw = set(get_form(node) for node in nodes if node.xpos and ('LUW.' in node.xpos))
print(sorted(luw))
len(luw)


# In[47]:


hitt & luw_hitt


# In[48]:


hitt & luw


# In[49]:


luw & luw_hitt


# In[50]:


luw_hitt


# In[51]:


set(node.xpos for node in nodes if node.xpos and ('LUW||HITT' in node.xpos or 'LUW/HITT' in node.xpos))


# In[52]:


set((get_form(node), node.xpos, node.gloss) for node in nodes if node.xpos and ('LUW||HITT' not in node.xpos and '||' in node.xpos))


# In[53]:


set((get_form(node), node.xpos, node.gloss) for node in nodes if node.xpos and ('(STF)' in node.xpos))


# ### Hurrian genitive

# In[54]:


print_prepr_gfs([gf for gf in prepr_gfs if 'HURR.GEN' in gf])


# ### Hurrian essive

# In[55]:


print_prepr_gfs([gf for gf in prepr_gfs if 'HURR.ESS' in gf])


# ### Hurrian absolutive

# In[56]:


print_prepr_gfs(['DN.HURR.ABS',
                 'HURR.ABS.SG',
                 'HURR.ABS.PL',
                 'DN.HURR.ABS.SG',
                 'DN.HURR.ABS.PL'])


# In[57]:


sg = set(get_form(node) for node in by_prepr_gf['HURR.ABS.SG'])
no = set(get_form(node) for node in by_prepr_gf['DN.HURR.ABS'])


# In[58]:


sg & no


# ### Preposition

# In[59]:


for node in bygf.get('GEN', [])[:1]:
     print(node.segment.sentence)


# In[60]:


modify_values(len, group_by(lambda x: x, (node.xpos for node in nodes if node.form == 'ŠA')))


# ### Checking

# In[61]:


set((get_form(node), node.gloss) for node in bygf.get('LUW.NOM/ACC.SG||HITT.ACC.SG.C',[]))


# In[62]:


set((get_form(node), node.gloss) for node in bygf.get('LUW.NOM/ACC.SG', []))


# In[63]:


set(bygf.get('LUW.NOM/ACC.SG||HITT.ACC.SG.C', []))


# In[64]:


set((get_form(node), node.gloss) for node in bygf[None])


# In[65]:


set(bygf.get('HITT.ADJG.GEN.SG', []))


# In[66]:


set(str(node.misc) for node in nodes if node.lemma == 'mân')


# In[67]:


for tag in gfs:
    if 'NOM/ACC' in tag or 'N/A' in tag:
        print(tag)


# In[68]:


set((get_form(node), node.gloss) for node in bygf.get('LUW.NOM/ACC.SG', []))


# In[69]:


from library.iterable import group_by, modify_values
from functools import partial
bycorrgf = group_by(lambda node: preprocess_gramm_form(corr(node.xpos)) if node.xpos is not None else None, nodes)
len(bycorrgf)


# In[70]:


set((get_form(node), node.gloss, node.xpos) for node in bycorrgf.get('N/A.PL.N', []))


# In[71]:


bygf.get('ALL, VOC.SG, NOM.PL.N, ACC.PL.N', [])


# ## Modifications

# In[72]:


def get_xpos(pos: str, gf: str):
    if pos == gf:
        return None
    elif pos + '.' in gf:
        return gf.replace(pos + '.', '')
    else:
        return gf.replace(pos, '')


# In[73]:


for node in nodes:
    if node.xpos is not None:
        gf = preprocess_gramm_form(corr(node.xpos))
        corr_gf = correct_gramm_form(gf)
        try:
            decomponed, struct = dec('any', corr_gf)
        except CannotParseGrammForm:
            print(node)
            continue
        if 'pos' in decomponed:
            pos = decomponed['pos']
            node.upos = pos
            del decomponed['pos']
            node.xpos = get_xpos(pos, corr_gf)
        elif struct is not None:
            node.upos = struct.upper()
            node.xpos = corr_gf
        node.feats = decomponed


# In[74]:


doc[152]


# In[75]:


dec('any', '3SG.PRS')


# In[76]:


dec('any', 'NOM.SG')


# In[77]:


doc[167]


# ## Akkadian enclitics and relators

# ### Akkadian enclitics

# #### Corrections

# In[78]:


from hit_morph.struct.encl_chain import EnclChain

modified = list()
modifications = list[str]()
quirky = list()

for node in nodes:
    exp = node.form
    ec = node.attached_enclitics_tag
    if exp in {'A-ŠAR-ŠU', 'AŠ-RI-ŠU'}:
        old = 'POSS.3SG.ACC.SG.N'
        new = 'DEM2/3.GEN.SG'
    elif exp in {'A-ŠAR-ŠU-NU', 'A-ŠAR-ŠU-NUpat'}:
        old = 'POSS.3PL.ACC.PL.N'
        new = 'DEM2/3.GEN.PL'
    else:
        continue
    if ec is None:
        node.attached_enclitics_tag = new
        quirky.append(node.segment)
    else:
        if ec == old:
            node.attached_enclitics_tag = new
            modified.append(node.segment)
        else:
            new = '='
        modifications.append('{0:20} {1:25} {2:20}'.format(exp, old, new))


# In[79]:


len(quirky), len(modified)


# In[82]:


grouped = group_by(lambda x: x, modifications)
for key, values in grouped.items():
    print(key, '({0})'.format(len(values)), sep='\t')


# #### Analytics

# In[83]:


gfs = set(node.attached_enclitics_tag for node in doc.wordforms if node.attached_enclitics_tag)
len(gfs)


# In[84]:


gfs


# In[85]:


from library.iterable import group_by, modify_values
from functools import partial
bygf = group_by(lambda node: node.attached_enclitics_tag, filter(lambda node: node.attached_enclitics_tag, doc.wordforms))
len(bygf)


# In[86]:


for gf in sorted(gfs):
    print('{0:25} {1:10} {2}'.format(gf, '({0})'.format(len(bygf[gf])),
                                     ', '.join(list(set(str(node.form) for node in bygf[gf]))[:5])))


# In[87]:


corr = Corrector(path.join(HM, 'Corrections/Enclitics forms.txt'))
gs = GrammaticalSystem.from_file(path.join(hm, 'Tag structure/Enclitics grammatical system.txt'))
dec = Decomponer.from_file(path.join(hm, 'Tag structure/HFR Enclitics decomponer.txt'), gs.properties)


# In[88]:


errs = set()
for gf in gfs:
    preprocessed = preprocess_gramm_form(corr(gf))
    try:
        dec('any', preprocessed)
    except CannotParseGrammForm:
        pass
    errs.add((gf, preprocessed))
len(errs)


# In[89]:


for x, y in sorted(errs):
    print("{0:25} {1:20} {2:6} {3}".format(x, y if x!=y else '=', str(len(bygf[x])), ', '.join(c.segment.exponent for c in bygf[x])))


# #### Mofifications

# In[90]:


modified = list[tuple[str, Morpholex]]()

for node in nodes:
    gf = node.attached_enclitics_tag
    corr_gf = preprocess_gramm_form(corr(gf))
    if corr_gf != gf:
        node.attached_enclitics_tag = corr_gf
        modified.append((gf, node))

len(modified)


# In[91]:


for gf, node in set(modified):
    print('{0:25} {1}'.format(gf, node))


# ### Relators

# #### Analytics

# In[92]:


gfs = set(node.relators for node in doc.wordforms if node.relators)
len(gfs)


# In[93]:


gfs


# In[94]:


from library.iterable import group_by, modify_values
from functools import partial
bygf = group_by(lambda node: node.relators, filter(lambda node: node.relators, doc.wordforms))
len(bygf)


# In[95]:


for gf in sorted(gfs):
    print('{0:25} {1:10} {2}'.format(gf, '({0})'.format(len(bygf[gf])),
                                     ', '.join(list(set(str(node.form) for node in bygf[gf]))[:5])))


# In[96]:


corr = Corrector(path.join(HM, 'Corrections/Enclitics forms.txt'))
gs = GrammaticalSystem.from_file(path.join(hm, 'Tag structure/Enclitics grammatical system.txt'))
dec = Decomponer.from_file(path.join(hm, 'Tag structure/HFR Enclitics decomponer.txt'), gs.properties)


# In[97]:


errs = set()
for gf in gfs:
    preprocessed = preprocess_gramm_form(corr(gf))
    try:
        dec('any', preprocessed)
    except CannotParseGrammForm:
        pass
        errs.add((gf, preprocessed))
len(errs)


# In[98]:


for x, y in sorted(errs):
    print("{0:25} {1:20} {2:6} {3}".format(x, y if x!=y else '=', str(len(bygf[x])), ', '.join(c.segment.exponent for c in bygf[x])))


# #### Mofifications

# In[99]:


modified = list[tuple[str, Morpholex]]()

for node in nodes:
    gf = node.relators
    corr_gf = preprocess_gramm_form(corr(gf))
    if corr_gf != gf:
        node.relators = corr_gf
        modified.append((gf, node))

len(modified)


# In[100]:


for gf, node in set(modified):
    print('{0:25} {1}'.format(gf, node))


# ## Enclitics

# ### Extracting grammatical forms

# In[101]:


encl_chains = [clitic_complex.encl_chain
               for clitic_complex in doc.clitic_complexes
               if clitic_complex.encl_chain is not None]


# In[102]:


from itertools import chain
enclitics = set()
for ec in encl_chains:
    try:
        enclitics |= (
            set(zip(ec.exponents.split('='), ec.tags.split('='), strict=True))
        )
    except (ValueError, AttributeError):
        print(ec)
print(len(enclitics))


# In[103]:


print(sorted(enclitics))


# In[104]:


from itertools import chain
gfs = set(e[1] for e in enclitics)
len(gfs)


# In[105]:


gfs


# In[106]:


from library.iterable import group_by_many, modify_values
from functools import partial
bygf = group_by(lambda e: e[1], enclitics)
len(bygf)


# In[107]:


set(ec.tags for ec in encl_chains if ec.exponents is None)


# In[108]:


from collections import Counter

for gf in sorted(gfs):
    print('{0:25} {1:10} {2}'.format(gf, '({0})'.format(len(bygf[gf])),
                                     Counter(e[0] for e in bygf[gf])))


# In[111]:


[node for node in encl_chains if node.exponents and 'an' in node.exponents and 'OBPn' in node.tags]


# In[112]:


[node for node in encl_chains if node.exponents and '=an' in node.exponents and 'OBPs' in node.tags]


# In[113]:


for node in encl_chains:
    if node.exponents == 'ya=za=an' in node.exponents and node.tags == 'CNJadd=REFL=OBPs':
        print(node)
        node.tags = 'CNJadd=REFL=OBPn'
        print(node)


# In[114]:


set(node[0] for node in bygf['PPRO.3SG.D/L'])


# In[115]:


set(node[0] for node in bygf['PPRO.3PL.D/L'])


# ### Grammatical forms

# In[116]:


import gen_morph.gramm_forms.decomponer
reload(gen_morph.gramm_forms.decomponer)
from gen_morph.gramm_forms.decomponer import Decomponer


# In[117]:


corr = Corrector(path.join(HM, 'Corrections/Enclitics forms.txt'))
gs = GrammaticalSystem.from_file(path.join(hm, 'Tag structure/Enclitics grammatical system.txt'))
dec = Decomponer.from_file(path.join(hm, 'Tag structure/HFR Enclitics decomponer.txt'), gs.properties)


# In[118]:


errs = set()
for gf in gfs:
    preprocessed = preprocess_gramm_form(corr(gf))
    try:
        dec('any', preprocessed)
    except CannotParseGrammForm:
        pass
    if preprocessed != gf:
        errs.add((gf, preprocessed))
len(errs)


# In[119]:


for x, y in sorted(errs):
    print("{0:25} {1:25} {2:10} {3}".format(x, y if x!=y else '=', str(len(bygf[x])), ', '.join(c[0] for c in bygf[x])))


# ## Modifications

# In[120]:


for ec in encl_chains:
    ec.tags = '='.join(preprocess_gramm_form(corr(single)) for single in ec.tags.split('='))


# In[121]:


[ec.tags for ec in encl_chains if 'RLT.PL' in ec.tags]


# ## Final analytics

# In[124]:


for hashset in [
    set(node.upos for node in nodes),
    set(node.xpos for node in nodes),
    set((node.upos, node.xpos) for node in nodes)
]:
    print(len(hashset))


# In[125]:


grouped = group_by(lambda t: t[1], set((node.upos, node.xpos) for node in nodes))
for key, values in grouped.items():
    if len(values) > 1:
        print(key)
        for value in values:
            print('\t' + str(value[0]))
        print()


# ## Saving

# In[126]:


doc.save('{0}-decomponed-tags.txt'.format(CORPUS))


# In[ ]:




