cth="$1"
~/NeuralCanonicalSegmentation/env/bin/python ~/NeuralCanonicalSegmentation/src/get_log_probs.py "data/conllu/CTH ${cth}_XML_HFR.conllu" "log_probs/CTH ${cth}_XML_HFR" ~/Hittite/models/Classifier lemma upos gloss simple_label encl_chain det
