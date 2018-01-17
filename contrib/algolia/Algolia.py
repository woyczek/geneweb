#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, string, codecs, time, http.client
import socket
import getopt
import requests
import re
import json

#import urllib
from datetime import date
from time import strftime, sleep
hostname =  socket.gethostname() 
if hostname == "iMac-H" :
  from algoliasearch import algoliasearch

#############################################
# Debut
#############################################
    
# mettre à jour "../Chausey-CD/Gw/etc/Chausey/trl.txt"

now = date.today()
stamp = strftime("%Y-%m-%d %H:%M:%S")

def usage () :
  print (" Make-Algolia.py --base --size --index --passwd --chunk quiet ")
  
basename = 'Chausey'

try:
  opts, args = getopt.getopt(sys.argv[1:], ":hv", ["help", "base=", "password=", "size=", "index=", "chunk=", "quiet"])
except getopt.GetoptError as err:
  # print help information and exit:
  print(str(err)) # will print something like "option -a not recognized"
  print ('Funny option', sys.argv)
  usage()
  sys.exit(2)
maxIndex=100
startIndex=0
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
  elif o in ("-i", "--password"):
    password = a
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

print ('Make-algolia starting now : '+stamp)
print ('Params: base: %s, start: %d, maxIndex: %d, passwd: %s'%(basename, startIndex, maxIndex, password))
  
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

outFileF = './'+basename+'_private-chunk'+chunkNb+'.json'
outFileW = './'+basename+'_public-chunk'+chunkNb+'.json'
try :
  outf = open(outFileF, 'w', encoding='utf-8')
except IOError :
  print ('Cannot open '+outFileF)
  sys.exit(1)
try :
  outw = open(outFileW, 'w', encoding='utf-8')
except IOError :
  print ('Cannot open '+outFileW)
  sys.exit(1)

outf.write('[\n')
outw.write('[\n')
i = startIndex
totLength = 0
while i < maxIndex :
  dum = """
  if hostname == "iMac-H" :
    Url = "http://127.0.0.1:2317/"+basename+"?templ=algolia;i="+str(i)
    time.sleep(0.01) # delays in sec
  else :
    #on TuxDemo 
    Url = "http://demo.geneweb.tuxfamily.org/gw7/gwd?b="+basename+";templ=algolia;i="+str(i)
    time.sleep(1) # on TuxDemo
  #if not Quiet : print ('----- Doing : %s'%(Url))
  try :
    r = requests.get(Url)
    data = r.text
  except requests.exceptions.ConnectionError :
    time.sleep(1)
    print ("Sleep 1 sec and try again")
    r = requests.get(Url)
    data = r.text
  data = data.replace('<br>', '\n')
  errorfF = data.find('Requête incorrecte')
  erroreF = data.find('Incorrect request')
  """
  
  if hostname == "iMac-H" :
    Url = "http://127.0.0.1:2317/"+basename+"?templ=algolia;w="+password+";i="+str(i)
    time.sleep(0.01) # delays in sec
  else :
    #on TuxDemo 
    Url = "http://demo.geneweb.tuxfamily.org/gw7/gwd?b="+basename+";templ=algolia;w="+password+";i="+str(i)
    time.sleep(1) # on TuxDemo
  #if not Quiet : print ('----- Doing : %s'%(Url))
  try :
    r = requests.get(Url)
    data = r.text
  except requests.exceptions.ConnectionError :
    time.sleep(1)
    print ("Sleep 1 sec and try again")
    r = requests.get(Url)
    data = r.text
  data = data.replace('<br>', '\n')
  errorf = data.find('Requête incorrecte')
  errore = data.find('Incorrect request')

  if errorf < 0 and errore < 0:
    yes = data.find('stephanie+marie+elisabeth.0.grimaldixxxxx')
    if yes >=0 : print ('Data1:', data)

    is_not_visible = data.find ('is_not_visible=1')
    data = data.replace ('is_not_visible=1', '')
    data = data.replace ('is_not_visible=0', '')

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
    
    # cleanup image attribute
    imageb = data.find ('/separator/image/')
    if imageb >= 0 :
      imbeg = data.find('w='+password, imageb)
      imend = data.find('algolia', imbeg)
      if imbeg >= 0 and imend >= 0 :
        if yes >= 0 :
          print ('Part1:', imbeg, data[imbeg-20:imbeg+len('w='+password)])
          print ('Part2:', imend, data[imend+len('algolia'):imend+100])
        data = data[:imbeg+len('w='+password)]+data[imend+len('algolia'):]
    
    # suppress other tags in Notes
    noteb = data.find ('/separator/notes/')
    if yes >= 0 : print ('Noteb:', noteb, data[noteb:noteb+20])
    more = 1
    while more == 1 and noteb >= 0 :
      abeg = data.find ('<', noteb)
      aend1 = data.find ('>', abeg+1)
      if abeg < 0 : 
        more = 0
      else :
        data = data[:abeg]+data[aend1+1:]
    data = data.replace('\n\n', '\n')
    data = data.replace('\n\n', '\n')
    data = data.replace('\n\n', '\n')
    data = data.replace('\n\n', '\n')
    data = data.replace('\n\n', '\n')
    data = data.replace('\n ', '\n')
    data = data.replace('\n ', '\n')
    data = data.replace('\n ', '\n')
    data = data.replace('\n ', '\n')
    data = data.replace('\n ', '\n')
    data = data.replace('\n ', '\n')
    data = data.replace('\n ', '\n')
    data = data.replace('/separator/\n', '/separator/')
    data = data.replace('\n/separator/,', '/separator/,')
    if yes >=0 : print ('Data2:', data)

    # clean-up nonce in http:// to person
    # Depending on localhost or CGI mode, the nonce etrminates with ? or ;!!
    hrefb = data.find ('http://')
    nonceb = data.find ('_', hrefb)
    if hostname == "iMac-H" :
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
    if hostname == "iMac-H" :
      noncee = data.find ('?', nonceb)
    else :
      noncee = data.find (';', nonceb)
    if nonceb >= 0 and noncee >= 0 :
      data = data[:nonceb]+data[noncee:]
    if yes >=0 : print ('Data22:', data)
    
    # Remove templ=algolia; if any left
    data = data.replace ('templ=algolia;', '')
    
    # remplacer tous les " par \"
    data = data.replace ('"', '\\"')
    data = data.replace ('/separator/|/separator2/', '/separator//separator2/')
    data = data.replace ('/separator2/', '"')
    if yes >=0 : print ('Data23:', data)
    
    # loop on each repetitive attribute (Prénom, Places, Alias) to suppress doubles
    # beware : "locations": ["aaa, bbb", "ccc", "ddd"]
    data = data.replace (':  ', ': ')
    for attr in ['firstnames', 'locations', 'dates'] :
      if yes >=0 : print ('Attr:', attr)
      tag = '/separator/'+attr+'/separator/: /separator/'
      tagb = data.find (tag)
      tage = data.find ('/separator/,\n', tagb+1)
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
        for t in tagsList :
          if t != "" :
            if tagsNew != "" :
              tagsNew = tagsNew+", "+t
            else :
              tagsNew = t
        if attr == "locations" :
          tagsNew = '['+tagsNew+']'
        if yes >=0 : print ('TagsN:', tagsNew)

        # compute average date
        daterange = ""
        if attr == "dates" :
          tagsNewList = tagsNew.split(',')
          tot = 0
          for d in tagsNewList :
            d = d.strip()
            if d != "" :
              tot = tot + int(d)
          average = tot/len(tagsNewList)
          if average > 0 :
            daterange = '/separator/daterange/separator/: %d,\n'%average
          else :
            daterange = ""
          #print ('Dates:', tagsNewList, daterange)
        # insert daterange
        data = data[:tagb]+daterange+tag+tagsNew+data[tage:]
      else :
        if yes >=0 : print ('No tagb:', tag, data)

    if yes >=0 : print ('Data3:', data)
    data = data.replace ('/separator/[', '[')
    data = data.replace (']/separator/', ']')
    data = clean_data (data)
    if data != "" :
      if is_not_visible >= 0 :
        outw.write (data+'\n')
      else :
        outf.write (data+'\n')
    comma = data.find (',')
    print ('I=', i, data[12:comma])
    totLength = totLength + len(data)
  i += 1

outf.write ('{ "objectID": "dummy-record", "dummy": ""}\n]\n')
outw.write ('{ "objectID": "dummy-record", "dummy": ""}\n]\n')
outf.close()
outw.close()
totK = totLength/1000
totM = totLength/1000000
if totLength < 1000 :
  print ('Finished: %.2f bytes'%totLength)
elif totLength < 1000000 :
  print ('Finished: %.2f Kbytes'%totK)
else:
  print ('Finished: %.2f Mbytes'%totM)

if hostname == "iMac-Hxx" and basename != "Grimaldi700" :
  print ('Start uploading '+outFileF+' and '+outFileW+' to Algolia')
  client = algoliasearch.Client("GMGUNOIT8M", 'd3a0bbe63a35c26867333b184f3b8d26')
  index = client.init_index(basename+'_private')
  batch = json.load(open(outFileF))
  index.add_objects(batch)

  index = client.init_index(basename+'_public')
  batch = json.load(open(outFileW))
  index.add_objects(batch)
  #index.set_settings({"searchableAttributes": ["names", "firstnames", "locations", "dates", "daterange"]})
  print ('Finished uploading to Algolia')


sys.exit(0)

#end


