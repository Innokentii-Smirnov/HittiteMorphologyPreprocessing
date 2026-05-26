from library.serializable import Serializable
String = str | None

class Morpholex(Serializable):
    sep = '@'

    def __init__(self, lemma: str, gloss: str, gramm_form: str, stem_class: str, det: str, upos: str,
                 relators: str = None,
                 attached_enclitics_tag: str = None,
                 exponent: str = None):
        self.lemma = lemma if lemma != '' else None
        self.gloss = gloss if gloss != '' else None
        self.gramm_form = gramm_form if gramm_form != '' else None
        self.stem_class = stem_class if stem_class != '' else None
        self.det = det if det != '' else None
        self.upos = upos if upos != '' else None
        self.misc = {'Det': self.det, 'Class': self.stem_class}
        self.relators = relators
        self.attached_enclitics_tag = attached_enclitics_tag
        self._exponent = exponent
        return
    
    @classmethod
    def copy(cls, other, gramm_form: str):
        return cls(other.lemma, other.gloss, gramm_form, other.stem_class, other.det, other.upos,
        other.relators, other.attached_enclitics_tag, other._exponent)
    
    def get_elements(self) -> tuple[String, String, String, String, String, String, String, String, String]:
        return (self.lemma, self.gloss, self.gramm_form, self.stem_class,
                self.det, self.upos, self.relators, self.attached_enclitics_tag,
                self._exponent)
    
    @classmethod
    def from_strings(cls, lemma: str, gloss: str, gramm_form: str,
                     stem_class: str, det: str, upos: str,
                     relators: str = None, attached_enclitics_tag: str = None, exponent: str = None):
        return cls(lemma, gloss, gramm_form, stem_class, det, upos, relators, attached_enclitics_tag, exponent)

    @property
    def xpos(self) -> String:
        return self.gramm_form
    
    @xpos.setter
    def xpos(self, value: str):
        self.gramm_form = value

    @property
    def form(self) -> str:
        return self.segment.exponent
    
    @form.setter
    def form(self, value: str):
        self.segment.exponent = value

    @property
    def simple_label(self) -> str:
        if self.upos is None:
            if self.xpos is None:
                return '<ERR>'
            else:
                return self.xpos
        elif self.xpos is not None:
            char = self.xpos[0]
            sep = '.' if char.isupper() or (char.isdigit() and not self.upos == 'DEM') else ''
            return sep.join([self.upos, self.xpos])
        else:
            return self.upos
    
    @property
    def label(self) -> str:
        label = self.simple_label
        if self.relators is not None:
            label = '.'.join([label, self.relators])
        if self.attached_enclitics_tag is not None:
            label = '_'.join([label, self.attached_enclitics_tag])
        return label
    
    @property
    def exponent(self) -> str:
        if self._exponent is not None:
            return self._exponent
        else:
            return self.segment.exponent
    
    @exponent.setter
    def exponent(self, value: str):
        self._exponent = value
    
