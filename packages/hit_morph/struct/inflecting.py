from library.brackets import debrace, in_braces
from library.exceptions import InvalidOperationException, MissingKeyException
from gen_morph.exceptions import CannotParseFormSet, CannotParseGrammForm
from hit_morph import corrections as corrs
from collections.abc import Iterable
from library.serializable import Serializable, StringStringDict
import re
sep = re.compile(r'\} *\{')

def parse_form(form: str | None) -> StringStringDict:
    form = corrs.form_set_corr(form)
    if form is not None and (form.startswith('{') != form.endswith('}')):
        raise CannotParseFormSet(form)

    if form is not None and in_braces(form):
        forms = StringStringDict()
        spl = sep.split(debrace(form))
        for x in spl:
            if '→' in x:
                try:
                    key, value = re.split(r' → ', x)
                except ValueError:
                    raise CannotParseFormSet(form)
                forms[key.strip()] = value

        gramm_forms = forms
    else:
        gramm_forms = StringStringDict({None: form})
    return gramm_forms

class Inflecting(Serializable):

    def __init__(self, gramm_forms: StringStringDict):
        self.gramm_forms = gramm_forms

    def get_elements(self) -> tuple[StringStringDict]:
        return self.gramm_forms,

    @classmethod
    def from_strings(cls, gramm_forms: str):
        return cls(StringStringDict.from_string(gramm_forms))
    
    def compute(self):
        self.gramm_forms = parse_form(self.gramm_forms)
