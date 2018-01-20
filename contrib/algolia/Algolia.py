#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, string, codecs, time, http.client
import socket
import getopt
import requests
import re
import json
hostname =  socket.gethostname() 
if hostname == "iMac-H" :
  from algoliasearch import algoliasearch

#import urllib
from datetime import date
from time import strftime, sleep

#############################################
# Debut
#############################################
    
# mettre à jour "../Chausey-CD/Gw/etc/Chausey/trl.txt"

now = date.today()
stamp = strftime("%Y-%m-%d %H:%M:%S")

def usage () :
  print (" Make-Algolia.py --base --size --index --chunk quiet ")
  
try:
  opts, args = getopt.getopt(sys.argv[1:], ":hv", ["help", "base=", "size=", "index=", "chunk=", "quiet"])
except getopt.GetoptError as err:
  # print help information and exit:
  print(str(err)) # will print something like "option -a not recognized"
  print ('Funny option', sys.argv)
  usage()
  sys.exit(2)
  
basename = ""
startIndex=0
size=10
chunkNb=""
Quiet = False

#print ('Opts : ', opts)
#print ('Args : ', args)

for o, a in opts :
  #print ('O, A :', o, a)
  if o == "-v":
    verbose = True
  elif o in ("-h", "--help"):
    usage()
    sys.exit()
  elif o in ("-b", "--base"):
    basename = a
  elif o in ("-s", "--size"):
    if a == "" :
      size = 0
    else :
      size = int(a)
  elif o in ("-i", "--index"):
    if a == "" :
      startIndex = 0
    else :
      startIndex = int(a)
  elif o in ("-i", "--chunk"):
    chunkNb = a
  elif o in ("-q", "--quiet"):
    Quiet = True
  else:
    assert False, "unhandled option"
    exit(3)

maxIndex = startIndex + size

#print ('Getopt test')
#sys.exit()

  
# init http connexion
hostIp = "127.0.0.1"
#hostIp = "192.168.1.12"
sleepDelay = 0.000

def clean_data (data) :
  data = data.replace ('/separator/', '"')
  data = data.replace ('<li>', ',')
  data = clean (data)
  data = data.replace ('\n,',': ')
  data = data.replace ('\n"','"')
  #data = data.replace (' ,', ', ')
  #data = data.replace ('\n',' ')
  #data = data.replace ('  ', ' ')
  #data = data.replace ('": ", ', '": "')
  #data = data.replace (' ", ', '", ')
  #data = data.replace (',", ', '", ')
  #data = data.replace ('}, ', '},')
  return (data)
  
def clean (html):
  """
    Strip HTML tags from any string and transfrom special entities
  """
  text = html
 
  # apply rules in given order!
  rules = [
    { r'>\s+' : u'>'},                  # remove spaces after a tag opens or closes
    { r'\s+' : u' '},                   # replace consecutive spaces
    { r'\s*<br\s*/?>\s*' : u'\n'},      # newline after a <br>
    { r'</(div)\s*>\s*' : u'\n'},       # newline after </p> and </div> and <h1/>...
    { r'</(p|h\d)\s*>\s*' : u'\n\n'},   # newline after </p> and </div> and <h1/>...
    { r'<head>.*<\s*(/head|body)[^>]*>' : u'' },     # remove <head> to </head>
    { r'<a\s+href="([^"]+)"[^>]*>.*</a>' : r'\1' },  # show links instead of texts
    { r'[ \t]*<[^<]*?/?>' : u'' },            # remove remaining tags
    { r'^\s+' : u'' },                  # remove spaces at the beginning
    { r'\n\n' : u'\n' }                 # remove double \n
  ]
 
  for rule in rules:
    for (k,v) in rule.items():
      regex = re.compile (k)
      text  = regex.sub (v, text)
 
  # replace special strings
  special = {
    '&nbsp;' : ' ', '&amp;' : '&', '&quot;' : '"',
    '&lt;'   : '<', '&gt;'  : '>'
  }
 
  for (k,v) in special.items():
    text = text.replace (k, v)
 
  return text  

def get_bvar (param) :
  bvarb = data.find (param+'=')
  bvare = data.find ('\n', bvarb+1)
  if bvarb >= 0 :
    bvar = data[bvarb+len(param)+1:bvare]
  else :
    print ('Missing %s in .gwf file'%param)
    sys.exit(1)
  return (bvar)


if basename == "" :
  basename = input ('Basename: ')
  maxIndex = int(input ('MaxIndex: '))
  startIndex = int(input('StartIndex: '))
  if startIndex == "" : startIndex = 0

print ('Make-algolia starting now : '+stamp)
print ('Params: base: %s, start: %d, maxIndex: %d'%(basename, startIndex, maxIndex))

 
outFileF = './'+basename+'_private-chunk'+chunkNb+'.json'
outFileV = './'+basename+'_public-chunk'+chunkNb+'.json'
gwfFile = os.environ['BASE_DIR']+'/'+basename+'.gwf'
try :
  outf = open(outFileF, 'w', encoding='utf-8')
except IOError :
  print ('Cannot open '+outFileF)
  sys.exit(1)
try :
  outv = open(outFileV, 'w', encoding='utf-8')
except IOError :
  print ('Cannot open '+outFileV)
  sys.exit(1)

try :
  gwff = open(gwfFile, 'r', encoding='utf-8')
except IOError :
  print ('Cannot open '+gwfFile)
  sys.exit(1)

data = gwff.read()
hostname = get_bvar ('algolia_hostname')
password = get_bvar ('algolia_passwd')
appId = get_bvar ('algolia_appid')
apiKey = get_bvar ('wizard_apikey')
is_cgi = get_bvar ('is_cgi')
gwff.close()

#print ('Password:', password)

outf.write('[\n')
outv.write('[\n')
i = startIndex
totLength = 0
while i < maxIndex :
  if is_cgi != "yes" :
    Url = "http://"+hostname+":2317/"+basename+"?templ=algolia;lang=en;w="+password+";i="+str(i)
    time.sleep(0.01) # delays in sec
  else :
    Url = "http://"+hostname+"/gwd?b="+basename+";templ=algolia;lang=en;w="+password+";i="+str(i)
    time.sleep(1) # delays in sec
  try :
    r = requests.get(Url)
    data = r.text
  except requests.exceptions.ConnectionError :
    time.sleep(1)
    print ("Sleep 1 sec and try again")
    r = requests.get(Url)
    data = r.text
  data = data.replace('<br>', '')
  errore = data.find('Incorrect request')

  if errore < 0:
    yes = data.find('albert.1.grimaldixxxxxx')
    if yes >=0 : print ('Data1:', data)

    is_not_visible = data.find ('is_not_visible=1')
    data = data.replace ('is_not_visible=1', '')
    data = data.replace ('is_not_visible=0', '')
    data = data.replace ('is_cgi=1', '')
    data = data.replace ('is_cgi=0', '')
    if yes >= 0 : print ('Is_cgi:', is_cgi)
    #suppress <a tags
    more = 1
    while more == 1 :
      abeg = data.find ('<a ')
      aend1 = data.find ('>', abeg+1)
      aend2 = data.find ('</a>', aend1+1)
      if abeg < 0 : 
        more = 0
      else :
        data = data[:abeg]+data[aend1+1:aend2]+data[aend2+4:]

    # suppress other tags in Notes
    noteb = data.find ('|notes|')
    if yes >= 0 : print ('Noteb:', noteb, data[noteb:noteb+20])
    more = 1
    while more == 1 and noteb >= 0 :
      abeg = data.find ('<', noteb)
      aend1 = data.find ('>', abeg+1)
      if abeg < 0 : 
        more = 0
      else :
        data = data[:abeg]+data[aend1+1:]
    data = data.replace('|\n', '|')
    data = data.replace('\n|,', '|,')
    if yes >=0 : print ('Data2:', data)

    # clean-up nonce in http:// to person
    # Depending on localhost or CGI mode, the nonce etrminates with ? or ;!!
    # http://localhost:2317/Grimaldi700_xmpnlttxa?w=w
    # http://demo.geneweb.tuxfamily.org/gw7/gwd?b=Grimaldi700_xmpnlttxa;
    hrefb = data.find ('http://')
    nonceb = data.find ('_', hrefb)
    if is_cgi != "yes" :
      noncee = data.find ('?', nonceb)
    else :
      noncee = data.find (';', nonceb)
    if nonceb >= 0 and noncee >= 0 :
      data = data[:nonceb]+data[noncee:]
      if yes >=0 : print ('Data21:', data)
    else :
      if yes >=0 : print ('Pas de changement', hrefb, nonceb, noncee)
    # and to image
    hrefb = data.find ('http://', noncee)
    nonceb = data.find ('_', hrefb)
    if is_cgi != "yes" :
      noncee = data.find ('?', nonceb)
    else :
      noncee = data.find (';', nonceb)
    if nonceb >= 0 and noncee >= 0 :
      data = data[:nonceb]+data[noncee:]
    if yes >=0 : print ('Data22:', data)
    
    # Remove templ=algolia; if any left
    data = data.replace ('templ=algolia;', '')
    # and :2317 in CGI mode
    if is_cgi == "yes" :
      data = data.replace (':2317', '')
    
    # remplacer tous les " par \"
    data = data.replace ('"', '\\"')
    # In notes, replace | by \|
    notesb = data.find ('|notes|: ')
    notese = data.find ('|,|notes_end|')
    if notesb >= 0 and notese >= 0 :
      notes = data[notesb+len('|notes|: ')+1:notese] # ignore first and last |
      notes = notes.replace ('|', '\\|')
      data = data[:notesb+len('|notes|: ')]+'|'+notes+'|, '+data[notese+len('|,|notes_end|'):]
    else :
      data = data.replace ('|notes_end|', '')
    if yes >=0 : print ('Data23:', notesb, notese, data)
    
    # loop on each repetitive attribute (Prénom, Places, Alias) to suppress doubles
    # beware : "locations": |aaa, bbb|ccc|ddd| -> ["aaa, bbb", "ccc", "ddd"]
    data = data.replace (':  ', ': ')
    for attr in ['firstnames', 'locations', 'dates', 'sources'] :
      if yes >=0 : print ('Attr:', attr)
      tag = '|'+attr+'|:'
      tagb = data.find (tag)
      tage = data.find ('|,', tagb+1)
      if tagb >= 0 :
        tags = data[tagb+len(tag):tage]
        tagsList = tags.split ('|')
        for t in tagsList :
          t = t.strip (' ')
        if yes >=0 : print ('TagsL:', tagsList)
        k = 0
        while k < len(tagsList) :
          j = 0
          while j < len(tagsList) :
            if tagsList[j].strip('"').find(tagsList[k].strip('"')) >= 0 and k != j :
              # suppress k if is part of j
              tagsList[k] = ""
            j += 1
          k += 1
        if yes >=0 : print ('TagsL:', tagsList)
        # Reconstruct tags list
        tagsNew = ""
        tagsCnt = 1
        if attr == 'firstnames' or attr == 'dates' :
          quotes = ''
        else :
          quotes = '"'
        for t in tagsList :
          t = t.strip()
          if t != '' :
            if tagsNew != '' :
              tagsNew = tagsNew+', '+quotes+t+quotes
            else :
              tagsNew = quotes+t+quotes
            tagsCnt += 1
        if yes >=0 : print ('TagsN:', tagsNew)

        # compute average date
        daterange = ""
        if attr == "dates" :
          tagsNewList = tagsNew.split(',')
          tot = 0
          for d in tagsNewList :
            d = d.strip()
            d = d.strip('"')
            if d != "" :
              tot = tot + int(d)
          average = tot/len(tagsNewList)
          if average > 0 :
            daterange = '"daterange": %d,\n'%average
          else :
            daterange = ""
          #print ('Dates:', tagsNewList, daterange)
        # insert daterange
        if attr == 'firstnames' or attr == 'dates' :
          tagsCnt = 1
        if tagsCnt > 1 :
          data = data[:tagb]+daterange+tag+' ['+tagsNew+']'+data[tage+1:]
        else :
          data = data[:tagb]+daterange+tag+' "'+tagsNew+'"'+data[tage+1:] 
      else :
        if yes >=0 : print ('No tagb:', tag, data)

    data = data.replace ('\\|', '§temporary_replacement§')
    data = data.replace ('|', '"')
    data = data.replace ('§temporary_replacement§', '|')

    data = data.replace (', "dummy": ""', '')
    data = data.replace ('"[', '[')
    data = data.replace (']"', ']')
    data = data.replace ('\n', ' ')
    data = data.replace ('  ', ' ')
    if yes >=0 : print ('Data3:', data)
    data = clean_data (data)
    if data != "" :
      if is_not_visible >= 0 :
        outv.write (data+'\n')
      else :
        outf.write (data+'\n')
    comma = data.find (',')
    print ('I=', i, data[:comma])
    totLength = totLength + len(data)
  i += 1
# Dummy record to close the chunk
outf.write ('{ "objectID": "dummy-record"}\n]\n')
outv.write ('{ "objectID": "dummy-record"}\n]\n')
outf.close()
outv.close()
totK = totLength/1000
totM = totLength/1000000
if totLength < 1000 :
  print ('Finished: %.2f bytes'%totLength)
elif totLength < 1000000 :
  print ('Finished: %.2f Kbytes'%totK)
else:
  print ('Finished: %.2f Mbytes'%totM)

if apiKey != "" and basename != "Grimaldi700xxx" :
  print ('Start uploading '+outFileF+' and '+outFileV+' to Algolia')
  client = algoliasearch.Client(appId, apiKey)
  index = client.init_index(basename)
  index.clear_index()
  batch = json.load(open(outFileF))
  index.add_objects(batch)
  batch = json.load(open(outFileV))
  index.add_objects(batch)

  index = client.init_index(basename+'_public')
  batch = json.load(open(outFileV))
  index.clear_index()
  index.add_objects(batch)
  #index.set_settings({"searchableAttributes": ["names", "firstnames", "locations", "dates", "daterange"]})
  print ('Finished uploading to Algolia')


sys.exit(0)

#end


