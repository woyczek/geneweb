#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, errno, sys, string
import datetime
import re
import getopt

global Table, DictSosa
global Gen

Table = []
Table = []
DictSosa = {}
DictLines = {}

def InitTable (n) :
	global Table
	size = 2**((n+1)/2)-1
	x = 0
	while x < size :
		y = 0
		Col = []
		while y < size :
			Col = Col +[0]
			y += 1
		Table = Table + [Col]
		x += 1		

def DoOneGen (basex, basey, size, n, sosa, sens, mode, Q, HI) :
	# basex basey : coordonnées du milieu du carré en construction
	# n : nombre de générations restant
	# sosa : sosa du centre du carré
    # Attention Table[y][x]
    # sens = 1 -> up
    # mode = 1 -> escalier
        
	global Table, DictSosa
	global Gen

	if n < 2:
		#print ("Nbr of Gen should be odd and greater or equal to 3", size, n)
		return
	#t1 = int ((2**((n+1)/2)-1)/2)   # t1 offset du sosa	
	t2 = (size-3)/4
	#print (Gen, size, n, t2)
	# quartiers, sens 1 = up (mère en bas), -1 = down (mère en haut)
	# 00 10
	# 01 11
	if mode == 1 :
		sens00 = 1
		sens01 = 1
		sens10 = 1
		sens11 = 1
	elif mode == -1 :
		sens00 = -1
		sens01 = -1
		sens10 =  1
		sens11 =  1
	else :
		print ("Wrong mode %s"%mode)
		
	#print ("Sosa=", sosa, "Mode=", mode, "Sens=", sens, "Basex=", basex, "Basey=", basey, "T2=", t2)

	if HI == "I" :	
		i  = basex
		j  = basey - sens*(t2+1)
		il = i
		jl = basey - t2
	else :
		i  = basex - sens*(t2+1)
		j  = basey
		il = basex - t2
		jl = j
	Table [i][j]   = sosa*2                     # father
	DictSosa[sosa*2] = [i, j]
	if HI == "I" :	
		y = jl
		while y < basey :
			Table [basex][y] = "|"
			y += 1
	else :
		x = il
		while x < basex :
			Table [x][basey] = "-"
			x += 1
	DictLines[sosa*2] = [il, jl]

	i = basex
	j = basey
	Table [i][j]   = sosa                       # sosa
	DictSosa[sosa] = [i, j]
	if HI == "I" :
		if Q == 00 or Q == 01 :
			il = basex + 1
			jl = basey
		else :
			il = basex - 2*t2 - 1 
			jl = basey
	else :
		if Q == 00 or Q == 10 :
			il = basex
			jl = basey + 1
		else :
			il = basex 
			jl = basey - t2 - 1
	DictLines[sosa] = [il, jl]
		

	if sosa != 1 :
		if HI == "I" :
			if Q == 00 or Q == 01 :
				x = basex + 1
				xm = basex + (size-1)/2 
			else :
				x = basex - (size-1)/2
				xm = basex -1
			while x <= xm :
				Table [x][basey] = "-"   
				x += 1
		else :
			if Q == 00 or Q == 10 :
				y = basey + 1
				ym = basey + (size-1)/2 
			else :
				y = basey - (size-1)/2
				ym = basey - 1 
			while y <= ym :
				Table [basex][y] = "|"  
				y += 1
		
	if HI == "I" :	
		i  = basex
		j  = basey + sens*(t2+1)
		il = i
		jl = basey+1
	else :
		i  = basex + sens*(t2+1)
		j  = basey
		il = basex+1
		jl = j
	Table [i][j] = sosa*2 + 1                    # mother
	DictSosa[sosa*2+1] = [i, j]
	if HI == "I" :	
		y = jl
		while y < basey+ t2 + 1 :
			Table [basex][y] = "|"
			y += 1
	else :
		x = il
		while x < basex + t2 + 1 :
			Table [x][basey] = "-"
			x += 1
	DictLines[sosa*2+1] = [il, jl]
	
	if n == 3 :
		i = basex - sens*1
		j = basey - sens*1
		Table [i][j] = sosa*4           # paternal grand father
		DictSosa[sosa*4] = [i, j]
		i = basex + sens*1
		Table [i][j] = sosa*4+1         # paternal grand mother
		DictSosa[sosa*4+1] = [i, j]
		i = basex - sens*mode*1
		j = basey + sens*1
		Table [i][j] = sosa*4+2         # maternal grand father
		DictSosa[sosa*4+2] = [i, j]
		i = basex + sens*mode*1
		j = basey + sens*1
		Table [i][j] = sosa*4+3         # maternal grand mother
		DictSosa[sosa*4+3] = [i, j]
		return

	if mode == 1 : 
		if HI == "I" :
			Q00 = sosa*4   # grand père paternel
			Q10 = sosa*4+1 # grand mère paternel
			Q01 = sosa*4+2 # grand père maternel
			Q11 = sosa*4+3 # grand mère maternelle
		else :
			Q00 = sosa*4   # grand père paternel
			Q10 = sosa*4+3 # grand mère paternel
			Q01 = sosa*4+1 # grand père maternel
			Q11 = sosa*4+2 # grand mère maternelle
		
	else :        # in mode colimacon, 
		Q00 = sosa*4   # grand père paternel
		Q10 = sosa*4+3 # grand mère paternel
		Q11 = sosa*4+2 # grand père maternel
		Q01 = sosa*4+1 # grand mère maternelle
	if HI == "I" :
		DoOneGen (basex-(t2+1), basey-(t2+1), (size-1)/2, n-2, Q00, sens00, mode, 00, HI)   # paternal grand father
		DoOneGen (basex+(t2+1), basey-(t2+1), (size-1)/2, n-2, Q10, sens10, mode, 10, HI)   # paternal grand mother
		DoOneGen (basex-(t2+1), basey+(t2+1), (size-1)/2, n-2, Q01, sens01, mode, 01, HI)   # maternal grand father
		DoOneGen (basex+(t2+1), basey+(t2+1), (size-1)/2, n-2, Q11, sens11, mode, 11, HI)   # maternal grand mother
	else :
		DoOneGen (basex-(t2+1), basey-(t2+1), (size-1)/2, n-2, Q00, sens00, mode, 00, HI)   # paternal grand father
		DoOneGen (basex+(t2+1), basey-(t2+1), (size-1)/2, n-2, Q10, sens10, mode, 10, HI)   # paternal grand mother
		DoOneGen (basex-(t2+1), basey+(t2+1), (size-1)/2, n-2, Q01, sens01, mode, 01, HI)   # maternal grand father
		DoOneGen (basex+(t2+1), basey+(t2+1), (size-1)/2, n-2, Q11, sens11, mode, 11, HI)   # maternal grand mother

def usage () :
	Usage = """
./H-tree.py [-g|--generations] [-m|--mode] [-x|--offsetx] [-y|--offsety] [-w|--width] [-h|--height] [-o|--orientation]
-g : nombred e générations (défaut 5)
-m :
  e = organisé en escalier (père à gauche) (défaut)
  c = organisé en colimaçon (père en tournant à gauche)
-x : offset x du coin haut gauche (défaut 10 pixels)
-y : offset  ydu coin haut gauche (défaut 10 pixels)
-w : largeur de la cellule (défaut 15)
-h : hauteur de la cellule (défaut 15)
-i : indices ou offset [oui|non](défaul oui)
-o : orientation en "H" (2-1-3 vertical) ou en "I" (2-1-3 horizontal)(défault)
"""
	print (Usage)

Mode = "e"
Gen = 5
Ox = 10
Oy = 10
Dx = 15
Dy = 15
Idx = "oui"
HI = "I"

try:
	opts, args = getopt.getopt(sys.argv[1:], "m:g:x:y:w:h:i:o:x", ["mode=", "generations=", "offsetx=", "offsety=", "width=", "height=", "indices=", "orientation"])
except getopt.GetoptError as err:
	# print help information and exit:
	print(str(err)) # will print something like "option -a not recognized"
	print ('Funny option', sys.argv)
	usage()
	sys.exit(2)

for o, a in opts :
	#print ('O, A :', o, a)
	if o in ("-m", "--mode"):
		Mode = a
	elif o in ("-g", "--generations"):
		Gen = int(a)
	elif o in ("-x", "--offsetx"):
		Ox = int(a)
	elif o in ("-y", "--offsety"):
		Oy = int(a)
	elif o in ("-w", "--width"):
		Dx = int(a)
	elif o in ("-h", "--height"):
		Dy = int(a)
	elif o in ("-i", "--indices"):
		Idx = a
	elif o in ("-o", "--orientation"):
		HI = a
	else:
		usage()
		exit(3)

if HI == "H" : Mode = "e" # pour l'instant !!

if int(Gen) > 16 :
	print ("Plus de 16 générations, pas raisonnable!!")
	sys.exit()

if Mode == "e" : 
	BMode = "escalier"
	Mode = 1
if Mode == "c" : 
	BMode = "colimaçon"
	Mode = -1
	#print ("Le mode colimacon ne fonctionne pas (encore), mais ça viendra!!")
	#sys.exit()

if Gen % 2 == -1 :
	print ("Nombre de générations impaires seulement")
	sys.exit()

print ('H-Tree for %s Generations in mode %s orientation "%s"'%(Gen, BMode, HI))

i = 0
if Gen % 2 == 0 : i = 1
InitTable (Gen + i)

size = 2**(int((Gen+2)/2))-1
sens = 1

DoOneGen ((size+1)/2-1, (size+1)/2-1, size, Gen, 1, 1, Mode, -1, HI)

di = (Gen+1)%2 # 1 si Gen est pair
for j in range(size) :
	strg = ""
	i = 0
	while i < size :
		if ((Gen+1)%2)*((i+1)%2) == 0 :
			if   Table[i][j] == "|" :
				strg = strg + "  |  "
			elif Table[i][j] == "-" :
				strg = strg + "-----"
			elif Table[i][j] == "l" :
				strg = strg + "lllll"
			elif Table[i][j] == "r" :
				strg = strg + "rrrrr"
			elif Table[i][j] == "t" :
				strg = strg + "ttttt"
			elif Table[i][j] == "b" :
				strg = strg + "bbbbb"
			elif Table[i][j] == 0 :
				strg = strg + "     "
			else :
				strg = strg + " "+("{:0>3d}".format(Table[i][j])) + " "
		i = i + 1
	strg = "["+strg[1:len(strg)-1]+"]"
	print (strg)

print ("")
if Idx == "oui" :
	s1 = "Indexes"
else :
	s1 = "Offsets"
print ("%s for %s generations."%(s1, Gen))
print ("0,0 is top left corner, positive x to the right positive y to the bottom")
#print ("Ng is the number of generations to be considered")
#print ("lN is the list for one level of sosa, starting at 1 (sosa=1) to Ng (sosa 2**(Ng-1) to 2**Ng-1)")
#print ("Table is offset by %s in X and %s in Y"%(Ox, Oy))
#print ("Cells dimentions are %s x %s"%(Dx, Dy))
l = 1
#while l <= Gen :
while l <= 0 :
	strgx = "dx-%sg-l%s : /"%(Gen, l)
	strgy = "dy-%sg-l%s : /"%(Gen, l)
	s0 = 2**(l-1)
	sl = s0 # do sosa from s0 to sl-1
	i=1
	while i <= sl :
		if Idx == "oui" :
			print (sl, l, i, 2**(l-1)-1+i)
			strgx = strgx + str(DictSosa[2**(l-1)-1+i][0]) + "/"
			strgy = strgy + str(DictSosa[2**(l-1)-1+i][1]) + "/"
		else :
			strgx = strgx + str(DictSosa[2**(l-1)-1+i][0]*Dx+Ox) + "/"
			strgy = strgy + str(DictSosa[2**(l-1)-1+i][1]*Dy+Oy) + "/"
		i += 1
	print (strgx)
	print (strgy)
	l += 1
	
strgx = "left%s : /"%Gen
strgy = "top%s  : /"%Gen
i = 1
while i < 2**(Gen) :
	if Gen%2 == 0 :
		strgx = strgx + str((DictSosa[i][0]-1)/2) + "/"
	else :
		strgx = strgx + str(DictSosa[i][0]) + "/"
	strgy = strgy + str(DictSosa[i][1]) + "/"
	i += 1
print (strgx)
print (strgy)

DictLines[1] = [0, 0]
strgx = "left%s_ : /"%Gen
strgy = "top%s_  : /"%Gen
i = 1
while i < 2**(Gen-2) :
	if Gen%2 == 0 :
		strgx = strgx + str((DictLines[i][0]-1)/2) + "/"
	else :
		strgx = strgx + str(DictLines[i][0]) + "/"
	strgy = strgy + str(DictLines[i][1]) + "/"
	i += 1
print (strgx)
print (strgy)
	
print ("Done")


sys.exit(0)


