input="$1"
output="$2"
export INPUT=$(realpath "$input")
export OUTPUT=$(realpath "$output")
export PYTHONPATH=$(realpath "packages")
export RESOURCES=$(realpath "resources")
export HM=$(realpath "1-Hittite-morphology")
python scripts/reading/1-Combine_xml.py && \
python scripts/reading/2-Sentence_tags.py && \
python scripts/reading/3-Parsing_sentences.py && \
python scripts/reading/4-From_xml.py && \
python scripts/preprocessing/Retokenization.py && \
python scripts/preprocessing/String_normalization.py && \
python scripts/preprocessing/Determinatives.py && \
python scripts/preprocessing/Lemmata.py && \
python scripts/preprocessing/Grammatical_form_structure.py && \
python scripts/preprocessing/Stem_classes_as_grammatical_forms.py && \
python scripts/preprocessing/Nominal_stem_classes.py && \
python scripts/preprocessing/Akkadian_pos_tags.py && \
python scripts/preprocessing/Sumerian_pos_tags.py && \
python scripts/preprocessing/Hittite_pos_tags.py && \
python scripts/preprocessing/Prepositions.py
