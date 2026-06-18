import os
from library.dm import DM

RESOURCES_DIRECTORY = os.getenv('RESOURCES')
if RESOURCES_DIRECTORY is None:
  raise RuntimeError('The envirnoment variable RESOURCES should be set \
    for package hit_morph to initialize properly.')
dm = DM(RESOURCES_DIRECTORY)



