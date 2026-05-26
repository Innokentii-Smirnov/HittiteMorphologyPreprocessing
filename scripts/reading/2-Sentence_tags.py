#!/usr/bin/env python
# coding: utf-8

# ### Imports

# In[1]:


import os
import sys

try:
    from google.colab import drive
    drive.mount('/content/drive')
    get_ipython().run_line_magic('env', 'HM=/content/drive/MyDrive/2-Hittite-morphology')
    sys.path.insert(1, "/content/drive/MyDrive/3-python-packages")
except ModuleNotFoundError:
    print(sys.path[1])
print(os.environ["HM"])


# In[2]:


from hit_morph.constants import CORPUS, VERSION, HM
print(CORPUS, VERSION, HM)


# ### Processing single file

# In[3]:


import re
from bs4 import BeautifulSoup, Tag

def process_text(text_tag: Tag, xml: BeautifulSoup):

    text_group = text_tag['path']
    text_name = text_tag['file']
    #text_name = text_tag.find('AO:Manuscripts').find('AO:TxtPubl').text

    tags = text_tag.find_all(['lb', 'clb', 'parsep', 'w'])

    #print(text_name)
    corpus: Tag = xml.corpus
    text = xml.new_tag('text', group=text_group)
    text['name'] = text_name
    corpus.append(text)

    new_par = True
    new_sent = True
    new_line = True
    par_no = 1
    sent_no = 1
    nr = 'unspec'
    lang = 'unspec'
    line = 'unspec'
    idx = 0

    for tag in tags:
        try:
            if tag.name == 'lb':
                new_line = True
                # The language of current line
                if 'lg' in tag.attrs:
                    lang = tag['lg']
                else:
                    lang = 'unk'
                # The id of current line
                if 'lnr' in tag.attrs:
                    line = re.sub(r'\{€\d(\+\d)?\}', '', tag['lnr']).strip()
                else:
                    line = 'unk'
            elif tag.name in {'parsep', 'parsep_dbl'}:
                new_par = True
            elif tag.name == 'clb' and 'lg' not in tag.attrs:
                new_sent = True
                if 'id' in tag.attrs:
                    nr = tag['id']
                else:
                    nr = 'unk'
            elif tag.name == 'w':
                tag['idx'] = idx
                idx += 1
                if new_par:
                    paragraph = xml.new_tag('par', no=str(par_no))
                    text.append(paragraph)
                    par_no += 1
                    new_par = False
                    new_sent = True
                if new_sent:
                    sentence = xml.new_tag('sent', no=str(sent_no))
                    sentence['nr'] = nr
                    sentence['langs'] = lang
                    sentence['lines'] = line
                    paragraph.append(sentence)
                    sent_no += 1
                    new_sent = False
                    new_line = False
                elif new_line:
                    if not sentence['langs'].endswith(lang):
                        sentence['langs'] += ', ' + lang
                    sentence['lines'] += ', ' + line
                    new_line = False
                if 'lg' in tag.attrs:
                    word_lang = tag.attrs['lg']
                else:
                    word_lang = lang
                if not sentence['langs'].endswith(word_lang):
                    sentence['langs'] += ', ' + word_lang
                sentence.append(tag)
        except:
            print(f'Имя файла: "{text_group}\\{text_name}"')
            print(f'Тэг: "{tag}"')
            raise


# ### Loading

# In[8]:


from os import path
source = os.getenv('OUTPUT')
path.exists(source)


# In[9]:


os.chdir(source)


# In[10]:


with open('Combined.xml', 'r', encoding='utf-8') as fin:
    contents = fin.read()


# In[11]:


len(contents)


# In[12]:


print(contents[1000:2000])


# In[13]:


combined = BeautifulSoup(contents, 'xml')


# In[14]:


for tag in 'text,parsep,clb,w'.split(','):
    print(len(combined(tag)))


# In[15]:


texts = combined.find_all('text')


# ### Test on single file

# In[16]:


text = texts[4]
print(str(text)[:1000])


# In[17]:


xml = BeautifulSoup('<corpus name="HFR"></corpus>', 'xml')
process_text(texts[0], xml)


# In[18]:


print(xml.prettify()[:1000])


# ### Multiple files

# In[19]:


from tqdm.auto import tqdm


# In[20]:


soup = BeautifulSoup('<corpus name="HFR" version="{0}"></corpus>'.format(VERSION), 'xml')
tq = tqdm(texts)


# In[21]:


for text_tag in tq:
    process_text(text_tag, soup)


# In[22]:


for tag in 'text,par,sent,w'.split(','):
    print(len(soup(tag)))


# In[23]:


from collections import defaultdict
pars = soup('par')
parlens = defaultdict(int)
for par in pars:
    parlens[len(list(par('sent')))]+=1


# In[24]:


sorted(parlens.items())


# In[25]:


sents = soup('sent')
sentlens = defaultdict(int)
for sent in sents:
    sentlens[len(list(sent('w')))]+=1


# In[26]:


sorted(sentlens.items())


# In[27]:


print(sents[165])


# In[28]:


for x in (sorted(sentlens.items(), reverse=True)):
    print(x)


# In[29]:


string = str(soup)


# In[30]:


print(string[:1000])


# In[31]:


from library.write import write_text
write_text(string, path.join(source, 'HFR.xml'))


# In[28]:


#from library.read import read_text
#new_string = read_text(path.join(source, 'HFR.xml'))


# In[29]:


#new_soup = BeautifulSoup(new_string, 'xml')


# In[30]:


#for tag in 'text,par,sent,w'.split(','):
    #print(len(new_soup(tag)))


# In[ ]:




