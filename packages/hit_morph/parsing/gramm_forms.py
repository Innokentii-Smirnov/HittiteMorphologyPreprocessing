import re
from .. import dm

def preprocess_gramm_form(form: str) -> str:
    if form is None:
        return form
    form = form.strip()
    form = form.replace('LUW||HITT', 'LUW/HITT')
    spl = re.split(r' ?\|\| ?', form)
    if len(spl) > 1:
        form = spl[1]
    form = form.removeprefix('…:')
    form = form.removeprefix('...:')
    form = form.removesuffix('(ABBR)')
    form = form.removesuffix('(!)')
    form = form.removesuffix('(?)')
    form = form.removesuffix('(UNM)')
    form = form.removesuffix('.')
    form = form.removesuffix('(STF)')
    form = form.replace('(!)','')
    form = form.replace('(?)','')
    form = form.removesuffix('!')
    form = re.sub(r'^FNL\(\-?\w*\)\.?', '', form)
    form = re.sub(r'(?<=\.)FNL\(\w+\)\.', '', form)
    return form


from gen_morph.tag_converter import TagConverter
with dm:
    conv = TagConverter('Tag converter.txt',
                        lambda cat, old: old.lower().capitalize()
                        if not (cat == 'Cat' or cat == 'Lang') else old.upper())

from .. import corrections as corrs
def parse_gramm_form(gramm_form: str) -> dict[str, str]:
    return conv(preprocess_gramm_form(corrs.gramm_form_corr(gramm_form)))
