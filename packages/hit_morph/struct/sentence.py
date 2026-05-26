from library.serializable import Serializable, SerializableList
from .segment import Segment
from bs4 import Tag
from hit_morph.check.wordform import check_wordform, Result
from alignment import align

class SegmentList(SerializableList):
    sep = ' \n\n'
    get_element = Segment.from_string
    
    def __str__(self) -> str:
        segments = [segment.text for segment in self]
        glosses = [str(segment.first.morpholex.gloss) for segment in self]
        labels = [segment.label for segment in self]
        return align([segments, glosses, labels])

class SentenceMetadata(Serializable):
    sep = '#\n'

    def get_elements(self) -> tuple[str, str, str, str]:
        return self.text_group, self.text_name, self.lines, self.langs
    
    @classmethod
    def from_strings(cls, text_group: str, text_name: str, lines: str, langs: str):
        return cls(text_group, text_name, lines, langs)
    
    def __init__(self, text_group: str, text_name: str, lines: str, langs: str):
        self.text_group = text_group
        self.text_name = text_name
        self.lines = lines
        self.langs = langs
    
    @classmethod
    def from_tag(cls, sent_tag: Tag):
        metadata = cls(
            sent_tag['text_group'],
            sent_tag['text_name'],
            sent_tag['lines'],
            sent_tag['langs']
        )
        return metadata
    
    def __str__(self):
        return ' '.join([self.text_group, self.text_name, self.lines])

class Sentence(Serializable):
    sep = '#\n\n'

    def get_elements(self) -> tuple[SentenceMetadata, SegmentList]:
        return self.metadata, self.segments
    
    @classmethod
    def from_strings(cls, metadata: str, segments: str):
        return cls(SentenceMetadata.from_string(metadata), SegmentList.from_string(segments))

    def assign_numbers_to_segments(self):
        for i, segment in enumerate(self.segments):
            segment.sentence = self
            segment.position = i

    def __init__(self, metadata: SentenceMetadata, segments: SegmentList):
        self.metadata = metadata
        self.segments = segments
        self.assign_numbers_to_segments()
    
    @classmethod
    def from_tag(cls, sent_tag: Tag):
        metadata = SentenceMetadata.from_tag(sent_tag)
        segments = SegmentList()
        tags = sent_tag.find_all('w')
        for tag in tags:
            try:
                segment = Segment.from_tag(tag)
                segments.append(segment)
            except:
                print(metadata)
                print(checked)
                print()
                for key, value in tag.attrs.items():
                    print("{0:10} '{1}'".format(key, value))
                raise
        return cls(metadata, segments)
    
    def __iter__(self):
        return iter(self.segments)
    
    def __len__(self):
        return len(self.segments)
    
    def __getitem__(self, idx: int):
        return self.segments[idx]
        
    def __str__(self) -> str:
        return '\n'.join((self.metadata.__str__(), self.segments.__str__()))
        
    @property
    def cth(self) -> int:
        cth = self.metadata.text_group
        cth = cth.removeprefix('CTH ')
        cth = cth.split("\\")[0]
        cth = cth.removesuffix('_XML')
        return int(cth)

