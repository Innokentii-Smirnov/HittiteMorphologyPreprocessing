from argparse import ArgumentParser
from hit_morph.struct.document import Document

parser = ArgumentParser(
  prog='to_conllu.py',
  description='Convert a corpus to CONLL-U format'
)
parser.add_argument('infile')
parser.add_argument('outfile')
args = parser.parse_args()

document = Document.load(args.infile)
ud_document = document.to_ud_document()
ud_document.store_conllu(args.outfile)
