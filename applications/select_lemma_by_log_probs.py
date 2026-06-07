from argparse import ArgumentParser
import os
from os import path
from hit_morph.struct.document import Document
from loading import load_all_log_probs, load_vocabs

parser = ArgumentParser(
  prog='select_lemma_by_log_probs.py',
  description='Select a lemma (and a morphological tag) for all words \
    in a document using probability distributions for different word attributes'
)
parser.add_argument('infile', help='Path to the input document')
parser.add_argument('outfile', help='Path to store the output document')
parser.add_argument('log_probs', help='A directory containing the probability distributions \
  as lists if numpy bidimensional arrays with the sentence length as first dimension \
  and number of attribute values as the second')
parser.add_argument('model_directory', help='A directory containing vocabularies of the models \
  that predicted the probability distributions')
args = parser.parse_args()

document = Document.load(args.infile)
log_probs = load_all_log_probs(args.log_probs)
vocabs = load_vocabs(args.model_directory)

document.select_lemma_by_log_probs(log_probs, vocabs)

outdir = path.dirname(args.outfile)
os.makedirs(outdir, exist_ok=True)
document.save(args.outfile)
