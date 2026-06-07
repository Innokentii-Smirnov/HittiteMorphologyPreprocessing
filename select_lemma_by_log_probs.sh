cth="$1"
python applications/select_lemma_by_log_probs.py "data/preprocessed/CTH ${cth}_XML_HFR/HFR-prep.txt" "data/lemmatized/CTH ${cth}_XML_HFR.txt" "log_probs/CTH ${cth}_XML_HFR" ~/Hittite/models/Classifier
