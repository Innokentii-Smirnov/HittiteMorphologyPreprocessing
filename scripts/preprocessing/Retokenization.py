#!/usr/bin/env python
# coding: utf-8

# ## Loading

# ### Reading

# In[1]:


import os
from importlib import reload
import hit_morph.struct.document
reload(hit_morph.struct.document)
from hit_morph.struct.document import Document
from hit_morph.constants import CORPUS, VERSION, HM
print(CORPUS, VERSION)
from os import path
corpus_dir = os.getenv('OUTPUT')
doc = Document.load(path.join(corpus_dir, '{0}.txt'.format(CORPUS)))


# In[2]:


len(doc)


# In[3]:


segments = doc.segments
len(segments)


# In[4]:


nodes = doc.wordforms
len(nodes)


# In[5]:


doc[2]


# ## Analytics

# In[6]:


from collections import Counter
Counter(segment.lang for segment in doc.segments)


# ## Prepositions

# ### Attached Akkadian prepositions (space in exponent)

# #### Startup

# In[7]:


from collections import Counter
lemma_counts = Counter(node.lemma for node in nodes)
form_counts = Counter(segment.exponent for segment in doc.segments)


# In[8]:


from library.iterable import group_by, modify_values
by_lemma = group_by(lambda node: node.lemma, nodes)
by_form = group_by(lambda segment: segment.exponent, doc.segments)


# In[9]:


from hit_morph.struct.sentence import Sentence, SegmentList
from hit_morph.struct.segment import Segment
from hit_morph.struct.clitic_complex import CliticComplex, CliticComplexDict
from hit_morph.struct.morpholex import Morpholex


# In[10]:


prepositional = [segment for segment in doc.segments if ' ' in segment.exponent]
len(prepositional)


# In[11]:


from functools import partial
from library.iterable import compone
lemmata = modify_values(partial(group_by, lambda node: node.lemma), group_by(lambda node: node.form, nodes))
modify_values(len, lemmata['LUGAL'])


# In[12]:


form_repl = {
    'ANA': 'A-NA',
    'A+NA': 'A-NA',
    'INA': 'I-NA',
    'I+NA': 'I-NA'
}


# In[13]:


from itertools import starmap


# In[14]:


for prep in sorted(set(segment.exponent.split(' ')[0] for segment in prepositional), key=form_counts.__getitem__, reverse=True):
    print('{0:15} {1:10} {2}'.format(prep,
                                     str(form_counts[prep]),
                                     ', '.join(starmap('{0}: {1}'.format, modify_values(len, lemmata.get(prep, dict())).items()))))


# #### IŠTU

if 'IŠ-TU' in lemmata:

    # In[15]:


    Counter(lemmata['IŠ-TU']['IŠTU'])


    # In[16]:


    lemmata['IŠ-TU'].get('ŠA', [])


    # In[17]:


    for morph in lemmata['IŠ-TU'].get('ŠA', []):
        morph.gloss = 'aus'
        morph.lemma = 'IŠTU'


# #### ANA

# In[18]:


Counter(lemmata['A-NA']['ANA'])


# In[19]:


lemmata['A-NA'].get('INA', [])


# In[20]:


for morph in lemmata['A-NA'].get('INA', []):
    morph.lemma = 'ANA'
    morph.gloss = 'zu'
    morph.xpos = 'PREP'


# #### PA-NI

if 'PA-NI' in lemmata:

    # In[21]:


    Counter(lemmata['PA-NI']['PĀNU'])


    # In[22]:


    lemmata['PA-NI'].get('1', [])


    # In[23]:


    lemmata['PA-NI'].get('PA-NI', [])


    # In[24]:


    for morph in lemmata['PA-NI'].get('1', []) + lemmata['PA-NI'].get('PA-NI', []):
        morph.lemma = 'PĀNU'
        morph.gloss = 'vor'
        morph.xpos = 'PREP'


    # In[25]:


    lemmata['PA-NI'].get('1', []) + lemmata['PA-NI'].get('PA-NI', [])


# #### ŠA and ŠÀ

if 'ŠA' in by_form:

    # In[26]:


    from itertools import chain
    for x in set(chain.from_iterable(segment.analyses for segment in by_form['ŠA'])):
        print(x)
        print()


# In[27]:

if 'ŠÀ' in by_form:

    for x in set(chain.from_iterable(segment.analyses for segment in by_form['ŠÀ'])):
        print(x)
        print()


# #### Continued

# In[28]:


from library.iterable import group_by_many, modify_values
grouped = group_by_many(lambda segment: [analysis.morpholex.gramm_form or '' for analysis in segment.analyses], prepositional)
for gramm_form, count in sorted(modify_values(len, grouped).items()):
    print('{0:35} {1:10} {2}'.format(gramm_form, str(count), ', '.join(sorted(set(segment.exponent for segment in grouped[gramm_form]))[:3])))


# In[29]:


modified = list[Sentence]()


# In[30]:


for segment in prepositional:
    if ' ' not in segment.translit:
        print(segment.exponent)
        print(segment.translit)
        print()


# In[31]:


for segment in prepositional:
    if ' ' not in segment.translit:
        print(segment.exponent)
        segment.translit += ' ' + segment.exponent.split(' ')[1]
        print(segment.translit)
        print()


# In[32]:


for segment in prepositional:
    assert ' ' in segment.translit
    if len(segment.translit.strip().replace('  ', ' ').split(' ')) > 2:
           print(segment)
           print()


# In[33]:


from warnings import warn
from library.iterable import composition
from library.serializable import StringList


# In[34]:


def detatch_preposition(segment: Segment):
    sentence = segment.sentence
    if sentence.segments[segment.position] is not segment:
        warn('The segment is not longer part of its sentence:\n\n{0}\n\nTerminating.'.format(segment))
        return
    modified.append(sentence)
    prep_exp, noun_exp = segment.exponent.split(' ')
    if prep_exp in form_repl:
        prep_exp = form_repl[prep_exp]
    prep_trans, noun_trans = segment.translit.strip().replace('  ', ' ').split(' ')

    prep = Segment(
        prep_exp, prep_trans, segment.lang, None, None,
        segment.old_selections, CliticComplexDict(), segment.idx,
        prep_exp, segment.new_selections, CliticComplexDict(),
        None, None, StringList(),
        None, None, StringList())
    noun = Segment(
        noun_exp, noun_trans, segment.lang, None, None,
        segment.old_selections, CliticComplexDict(), segment.idx,
        prep_exp, segment.new_selections, CliticComplexDict(),
        None, None, StringList(),
        None, None, StringList())
    prep_analyses = prep.options
    noun_analyses = noun.options

    for key, clitic_complex in segment.options.items():
        morph = clitic_complex.morpholex
        if morph.gramm_form and '_' in morph.gramm_form:
            spl = morph.gramm_form.split('_')
            first, second = '_'.join([spl[0]] + spl[2:]), spl[1]
            if any(second.strip().endswith(pos) for pos in {'POSP', 'ADV'}):
                noun_gf = first
                prep_gloss, prep_gf = second.split(':')
                prep_gf = 'PREP'
            else:
                noun_gf = morph.gramm_form
                prep_gloss = None
                prep_gf = 'PREP'
        else:
            noun_gf = morph.gramm_form
            prep_gloss = None
            prep_gf = 'PREP'
        if noun_gf:
            noun_gf = noun_gf.removeprefix('...:')
        prep_lemma = max(lemmata[prep_exp], key=composition(lemmata[prep_exp].__getitem__, len)) if prep_exp in lemmata else prep_exp
        prep_analysis = CliticComplex(Morpholex(prep_lemma,
                                                prep_gloss,
                                                prep_gf,
                                                None,
                                                None,
                                                None),
                                      None)
        noun_analysis = CliticComplex(Morpholex(morph.lemma,
                                                morph.gloss,
                                                noun_gf,
                                                morph.stem_class,
                                                morph.det,
                                                None),
                                      clitic_complex.encl_chain)
        prep_analyses[key] = prep_analysis
        noun_analyses[key] = noun_analysis

    del sentence.segments[segment.position]
    sentence.segments.insert(segment.position, prep)
    sentence.segments.insert(segment.position + 1, noun)
    sentence.assign_numbers_to_segments()


# In[35]:


ambiguous = list(filter(lambda segment: len(segment.analyses) > 1, prepositional))
ambiguous.sort(key=lambda segment: len(segment.analyses), reverse=True)
len(ambiguous)


# In[36]:


idx = 19
segm = ambiguous[idx]
segm


# In[37]:


detatch_preposition(segm)
SegmentList(segm.sentence.segments[segm.position:segm.position+2])


# In[38]:


segm = grouped['...:D/L.SG_vor:POSP'][0]
segm


# In[39]:


list(segm.options.items())


# In[40]:


detatch_preposition(segm)
SegmentList(segm.sentence.segments[segm.position:segm.position+2])


# In[41]:


segm = grouped['...:INS'][0]
segm


# In[42]:


detatch_preposition(segm)
SegmentList(segm.sentence.segments[segm.position:segm.position+2])


# In[43]:


for segment in prepositional:
    try:
        detatch_preposition(segment)
    except:
        print(segment)
        raise


# In[44]:


print(len(modified))


# ### Prepositions with case as tag (colon and ellipsis in tag)

# In[45]:


from hit_morph.struct.morpholex import Morpholex

def condition(morpholex: Morpholex):
    return morpholex.gramm_form is not None and '...:' in morpholex.gramm_form


# In[46]:


gf_with_colon = [segment for segment in doc.segments
         if any(condition(analysis.morpholex) for analysis in segment.analyses)]
len(gf_with_colon)


# In[47]:


not_all_gfs_with_colon = [segment for segment in gf_with_colon
         if any(not condition(analysis.morpholex) for analysis in segment.analyses)]
len(not_all_gfs_with_colon)


# In[48]:


all_gfs_with_colon = [segment for segment in gf_with_colon
         if all(condition(analysis.morpholex) for analysis in segment.analyses)]
len(all_gfs_with_colon)


# In[49]:


from library.iterable import group_by_many, modify_values
grouped = group_by_many(lambda segment: [analysis.morpholex.gramm_form or '' for analysis in segment.analyses], gf_with_colon)
for gramm_form, count in sorted(modify_values(len, grouped).items()):
    print('{0:35} {1:10} {2}'.format(gramm_form, str(count), ', '.join(sorted(set(segment.exponent for segment in grouped[gramm_form])))))


# In[50]:


from collections import Counter
Counter(len(segment.analyses) for segment in gf_with_colon)


# In[51]:


for segment in gf_with_colon:
    for clitic_complex in segment.analyses:
        morph = clitic_complex.morpholex
        if morph.gramm_form and morph.gramm_form.startswith('...:'):
            if morph.lemma is None:
                print(segment.exponent)


# In[52]:


for segment in gf_with_colon:
    for clitic_complex in segment.analyses:
        morph = clitic_complex.morpholex
        if morph.gramm_form and morph.gramm_form.startswith('...:'):
            morph.gramm_form = 'PREP'


# In[53]:


print(len(gf_with_colon))
for x in gf_with_colon[::25]:
    print(x)
    print()


# In[54]:


for x in not_all_gfs_with_colon:
    print(x)
    print()


# ## Glosses

# ### Genitive collocations

# In[55]:


from hit_morph.struct.morpholex import Morpholex

def condition(morpholex: Morpholex):
    return morpholex.gramm_form is not None and '+' in morpholex.gramm_form


# In[56]:


genitival = [segment for segment in doc.segments
         if '˽' in segment.exponent and any(condition(analysis.morpholex) for analysis in segment.analyses)]
len(genitival)


# In[57]:


not_all_genitival = [segment for segment in genitival
         if any(not condition(analysis.morpholex) for analysis in segment.analyses)]
len(not_all_genitival)


# In[58]:


all_genitival = [segment for segment in genitival
         if all(condition(analysis.morpholex) for analysis in segment.analyses)]
len(all_genitival)


# In[59]:


from collections import Counter
Counter(len(segment.analyses) for segment in genitival)


# In[60]:


from library.iterable import group_by_many, modify_values
grouped = group_by_many(lambda segment: [analysis.morpholex.gramm_form for analysis in segment.analyses], genitival)
for gramm_form, count in sorted(modify_values(len, grouped).items()):
    print('{0:35} {1:10} {2}'.format(
        gramm_form, str(count),
        ';\t'.join(sorted(set('{0:15} {1}'.format(segment.exponent, segment.analyses[0].morpholex.lemma, segment.translit) for segment in grouped[gramm_form])))))


# In[61]:


for prep in sorted(set(segment.exponent.split('˽')[0] for segment in genitival), key=form_counts.__getitem__, reverse=True):
    print('{0:15} {1:10} {2}'.format(prep,
                                     str(form_counts[prep]),
                                     ', '.join(starmap('{0}: {1}'.format, lemmata.get(prep, Counter()).items()))))


# In[62]:


from itertools import chain
'ḫazzi=u-' in chain.from_iterable(lemmata.values())


# In[63]:


print('ḫazziuaš' in lemmata)


# In[64]:


listed_lemmata = {
    'mukešnaš': 'muk=eššar',
    'ḫaziuaš': 'ḫazzi=u-',
    'KURantaš': 'KUR=ant-',
    'KUReantaš': 'KURe=ant-'
}


# In[65]:


def detatch_genitive(segment: Segment):
    sentence = segment.sentence
    if sentence.segments[segment.position] is not segment:
        warn('The segment is not longer part of its sentence:\n\n{0}\n\nTerminating.'.format(segment))
        return
    modified.append(sentence)
    gen_exp, noun_exp = segment.exponent.split('˽')
    gen_trans, noun_trans = segment.translit.split('˽')
    gen_analyses = CliticComplexDict()
    noun_analyses = CliticComplexDict()

    for key, clitic_complex in segment.options.items():
        morph = clitic_complex.morpholex
        assert '+' in morph.gramm_form
        first, second = morph.gramm_form.split('+')
        gen_gloss, gen_gf = first.split(':')
        noun_gloss, noun_gf = second.split(':')
        _, noun_lemma = morph.lemma.split('˽')

        noun_gf = noun_gf.removeprefix('...:')
        gen_lemma = max(lemmata[gen_exp], key=lemmata[gen_exp].__getitem__) if gen_exp in lemmata else listed_lemmata[gen_exp]
        gen_analysis = CliticComplex(Morpholex(gen_lemma,
                                                gen_gloss,
                                                gen_gf,
                                                None,
                                                None,
                                                None),
                                      None)
        noun_analysis = CliticComplex(Morpholex(noun_lemma,
                                                noun_gloss,
                                                noun_gf,
                                                morph.stem_class,
                                                morph.det,
                                                None),
                                      clitic_complex.encl_chain)
        gen_analyses[key] = gen_analysis
        noun_analyses[key] = noun_analysis

    prep = Segment(gen_exp, gen_trans, segment.lang, None, None, gen_analyses, segment.idx, segment.selections, None, None, None)
    noun = Segment(noun_exp, noun_trans, segment.lang, None, None, noun_analyses, segment.idx, segment.selections, None, None, None)
    del sentence.segments[segment.position]
    sentence.segments.insert(segment.position, prep)
    sentence.segments.insert(segment.position + 1, noun)
    sentence.assign_numbers_to_segments()


# In[66]:


segms = grouped.get('Anrufung:GEN.SG+Herr:D/L.SG', [])
segms


# In[67]:


#detatch_genitive(segm)
#SegmentList(segm.sentence.segments[segm.position:segm.position+2])


# In[68]:


for segm in grouped.get('Ritual:GEN.SG+Herr:NOM.PL.C', []):
    print(segm)


# In[69]:


#detatch_genitive(segm)
#SegmentList(segm.sentence.segments[segm.position:segm.position+2])


# In[70]:


for segm in grouped.get('Anrufung:GEN.SG+Herr:NOM.SG', []):
    print(segm)


# In[71]:


#detatch_genitive(segm)
#SegmentList(segm.sentence.segments[segm.position:segm.position+2])


# In[72]:


for segment in genitival:
    detatch_genitive(segment)


# In[73]:


print(len(genitival))
for x in set(x.sentence.segments[x.position] for x in genitival):
    print(x)
    print()


# ### Prepositions with case as tag (colon without ellipsis in tag)

# In[74]:


from hit_morph.struct.morpholex import Morpholex

def condition(morpholex: Morpholex):
    return morpholex.gramm_form is not None and ':' in morpholex.gramm_form


# In[75]:


gf_with_colon = [segment for segment in doc.segments
         if any(condition(analysis.morpholex) for analysis in segment.analyses)]
len(gf_with_colon)


# In[76]:


not_all_gfs_with_colon = [segment for segment in gf_with_colon
         if any(not condition(analysis.morpholex) for analysis in segment.analyses)]
len(not_all_gfs_with_colon)


# In[77]:


all_gfs_with_colon = [segment for segment in gf_with_colon
         if all(condition(analysis.morpholex) for analysis in segment.analyses)]
len(all_gfs_with_colon)


# In[78]:


from library.iterable import group_by_many, modify_values
grouped = group_by_many(lambda segment: [analysis.morpholex.gramm_form or '' for analysis in segment.analyses], gf_with_colon)
for gramm_form, count in sorted(modify_values(len, grouped).items()):
    print('{0:35} {1:10} {2}'.format(gramm_form, str(count),
                                     ', '.join(sorted(set(segment.exponent for segment in grouped[gramm_form])))))


# In[79]:


from collections import Counter
Counter(len(segment.analyses) for segment in gf_with_colon)


# In[80]:


for segment in gf_with_colon:
    for clitic_complex in segment.analyses:
        morph = clitic_complex.morpholex
        if condition(morph):
            match morph.gramm_form.split('+'):
                case main, tail:
                    print('Disregardging: ' + tail)
                case main,:
                    pass
                case _:
                    raise ValueError()
            gloss, gramm_form = main.split(':')
            if morph.gloss is None:
                morph.gloss = gloss
            elif morph.gloss != gloss:
                print('Mismatch: {0} != {1}'.format(morph.gloss, gloss))
            morph.gramm_form = gramm_form
            print(morph.gloss, morph.gramm_form)


# In[81]:


print(len(gf_with_colon))
for x in gf_with_colon[::25]:
    print(x)
    print()


# ## Enclitics

# ### Corrections

# In[82]:


for clitic_complex in doc.clitic_complexes:
    encl_chain = clitic_complex.encl_chain
    if encl_chain is not None and encl_chain.tags is None:
        print(clitic_complex)
        if encl_chain.exponents == 'kkan':
            encl_chain.tags = 'OBPk'
        elif encl_chain.exponents == 'za':
            encl_chain.tags = 'REFL'
        print(clitic_complex)


# In[83]:


from gen_morph.exceptions import CannotParseEnclChain

errs = set()
for clitic_complex in doc.clitic_complexes:
    encl_chain = clitic_complex.encl_chain
    if encl_chain is not None:
        try:
            clitic_complex.encl_chain.check()
        except CannotParseEnclChain:
            errs.add(clitic_complex)

len(errs)


# In[84]:


errs


# ### Relators

# In[85]:


from hit_morph.struct.clitic_complex import CliticComplex
from hit_morph.struct.morpholex import Morpholex
from hit_morph.struct.encl_chain import EnclChain

modified = list[CliticComplex]()

for clitic_complex in doc.clitic_complexes:
    node, encl_chain = clitic_complex.get_elements()
    if node.gramm_form is not None:
        idx = node.gramm_form.find('.RLT')
        if idx != -1:
            relators = node.gramm_form[idx+1:]
            node.gramm_form = node.gramm_form[:idx]
            node.relators = relators
            modified.append(clitic_complex)

len(modified)


# In[86]:


for x in modified:
    print('{0:60} {1}'.format(*map(repr, x.get_elements())))


# In[87]:


# Hurrian morphology:
# ui ~ ue ~ pe ~ pi GEN
# na ~ a RLT.PL.ABS
# ni-pi ~ ne-ue ~ ni-ue RLT.SG-GEN


# ### Correction

# In[88]:


for node in nodes:
    if node.xpos == 'CONJ + PPRO.3SG.D/L':
        print(node.segment)


# In[89]:


for node in nodes:
    if node.xpos == 'CONJ + PPRO.3SG.D/L':
        node.xpos = 'CNJ=PPRO.3SG.D/L'
        node.lemma += '=šši'
        mansi = node
        print(node.segment)


# ### Analytics

# In[90]:


from library.iterable import count
count(lambda node: node.gramm_form and '_' in node.gramm_form, doc.wordforms)


# In[91]:


s = set()
errs = list[CliticComplex]()

for clitic_complex in doc.clitic_complexes:
    node, encl_chain = clitic_complex.get_elements()
    if node.gramm_form is not None:
        if '=' in node.gramm_form:
            sep_index = node.lemma.find('=')
            if sep_index == -1 or node.lemma.endswith('-') or sep_index == len(node.lemma) - 1:
                errs.append(clitic_complex)
                continue
            gramm_form, encl_gramm_forms = node.gramm_form.split('=', 1)
            lemma, encl_lemmata = node.lemma.split('=', 1)
            s.add((encl_lemmata, encl_gramm_forms))


# In[92]:


errs


# In[93]:


counter = Counter(node.lemma for node in doc.wordforms)
print(counter['KÙ.BABBAR='])
print(counter['KÙ.BABBAR'])


# In[94]:


Counter(cc.encl_chain for cc in doc.clitic_complexes if cc.morpholex.lemma == 'KÙ.BABBAR=')


# In[95]:


for cc in errs:
    node = cc.morpholex
    if '=POSS.' in node.gramm_form:
        node.gramm_form = node.gramm_form.replace('=POSS', '_POSS')
        continue
    elif node.gramm_form.endswith('=FOC'):
        assert node.lemma == 'mukišn='
        node.lemma = 'mukeššar=pat'
    elif node.gramm_form.endswith('=CNJadd'):
        if node.lemma.endswith('='):
            node.lemma += 'ya'
        else:
            node.lemma += '=ya'
        print(node.lemma)
    elif node.gramm_form.endswith('=CNJctr'):
        node.lemma += '=ma'
        print(node.lemma)


# In[96]:


s = set()
errs = list[CliticComplex]()

for clitic_complex in doc.clitic_complexes:
    node, encl_chain = clitic_complex.get_elements()
    if node.gramm_form is not None:
        if '=' in node.gramm_form:
            sep_index = node.lemma.find('=')
            if sep_index == -1 or node.lemma.endswith('-') or sep_index == len(node.lemma) - 1:
                errs.append(clitic_complex)
                continue
            gramm_form, encl_gramm_forms = node.gramm_form.split('=', 1)
            lemma, encl_lemmata = node.lemma.split('=', 1)
            s.add((encl_lemmata, encl_gramm_forms))


# In[97]:


errs


# In[98]:


for l, g in s:
    assert l != ''
    assert g != ''
    assert len(l.split('=')) == len(g.split('='))
    print('{0:20} {1}'.format(l, g))


# ### Detach enclitics

# In[99]:


from library.iterable import count
count(lambda node: node.gramm_form and '_' in node.gramm_form, doc.wordforms)


# In[100]:


created = list[CliticComplex]()
modified = list[CliticComplex]()
errs = list[CliticComplex]()

for clitic_complex in doc.clitic_complexes:
    node, encl_chain = clitic_complex.get_elements()
    if node.gramm_form is not None:
        if '=' in node.gramm_form:
            sep_index = node.lemma.find('=')
            if sep_index == -1 or node.lemma.endswith('-') or sep_index == len(node.lemma) - 1:
                errs.append(clitic_complex)
                raise ValueError(clitic_complex)
            node.gramm_form, encl_gramm_forms = node.gramm_form.split('=', 1)
            node.lemma, encl_lemmata = node.lemma.split('=', 1)
            if encl_chain is None:
                clitic_complex.encl_chain = EnclChain(encl_lemmata, encl_gramm_forms, None)
                created.append(clitic_complex)
            else:
                encl_chain.exponents = '='.join([encl_lemmata, encl_chain.exponents])
                encl_chain.tags = '='.join([encl_gramm_forms, encl_chain.tags])
                modified.append(clitic_complex)

print(len(created), len(modified))


# In[101]:


set(cc.encl_chain for cc in modified)


# In[102]:


set(cc.encl_chain for cc in created)


# In[103]:


from library.iterable import count
count(lambda node: node.gramm_form and '_' in node.gramm_form, doc.wordforms)


# In[104]:


from hit_morph.struct.clitic_complex import CliticComplex
from hit_morph.struct.morpholex import Morpholex
from hit_morph.struct.encl_chain import EnclChain

modified = list[CliticComplex]()
for clitic_complex in doc.clitic_complexes:
    node, encl_chain = clitic_complex.get_elements()
    if node.gramm_form is not None:
        if '_' in node.gramm_form:
            node.gramm_form, encl_gramm_forms = node.gramm_form.split('_', 1)
            node.attached_enclitics_tag = encl_gramm_forms
            modified.append(node)

len(modified)


# In[105]:


set(modified)


# In[106]:


for x in modified[::10]:
    print(x)


# In[107]:


from gen_morph.exceptions import CannotParseEnclChain

errs = set()
for clitic_complex in doc.clitic_complexes:
    ec = clitic_complex.encl_chain
    if ec is not None:
        try:
            clitic_complex.encl_chain.check()
        except CannotParseEnclChain:
            errs.add(clitic_complex)

len(errs)


# In[108]:


for x in errs:
    print(x.morpholex)
    print(x.encl_chain)
    print()


# ## Saving

# In[109]:


doc.save(path.join(corpus_dir, '{0}-retokenized.txt'.format(CORPUS)))


# In[110]:


for segment in doc.segments:
    assert segment.idx != -1


# In[111]:


print(sorted(set(segment.idx for segment in doc.segments)))


# In[ ]:




