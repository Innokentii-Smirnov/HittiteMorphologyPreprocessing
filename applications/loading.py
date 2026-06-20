import os
from os import path
import numpy as np
from numpy import ndarray
from library.dm import DM
from library.read import read_list

def load_log_probs(filename: str) -> list[ndarray]:
  with open(filename, 'rb') as fin:
    log_probs: list[ndarray] = np.load(fin, allow_pickle=True)
  return log_probs

def load_all_log_probs(directory: str) -> dict[str, list[ndarray]]:
  all_log_probs = dict[str, list[ndarray]]()
  attributes = map(lambda file_name: path.splitext(file_name)[0], os.listdir(directory))
  with DM(directory):
    for attribute in attributes:
      curr_log_probs = load_log_probs('{0}.npy'.format(attribute))
      all_log_probs[attribute] = curr_log_probs
  return all_log_probs

def load_vocabs(model_directory: str) -> dict[str, dict[str | None, int]]:
  vocabs = dict[str, dict[str | None, int]]()
  attributes = map(lambda file_name: path.splitext(file_name)[0], os.listdir(model_directory))
  for attribute in attributes:
    directory = path.join(model_directory, attribute, 'Vocabularies')
    assert path.exists(directory), 'No vocabulary found for attribute "{0}".'.format(attribute)
    with DM(directory):
      elems = read_list('{0}.txt'.format(attribute))
    vocabs[attribute] = {elem if elem != '<NO>' else None: i for i, elem in enumerate(elems)}
  return vocabs
