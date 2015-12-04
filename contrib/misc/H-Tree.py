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

def set_grd_parents (mode, HI, sosa) : # pour dernier niveau
	if mode == 1 : # mode escalier
		if HI == "I" : # grand père à gauche
			Q00 = sosa*4   # grand père paternel (4)
			Q01 = sosa*4+1 # grand père maternelle (6)
			Q10 = sosa*4+2 # grand mère paternel (5)
			Q11 = sosa*4+3 # grand mère maternelle (7)
		else :         # grand père en haut
			Q00 = sosa*4   # grand père paternel (4)
			Q01 = sosa*4+2 # grand mère paternelle (5)
			Q10 = sosa*4+1 # grand père maternel (6)
			Q11 = sosa*4+3 # grand mère maternelle (7)
	else :        # in mode colimacon, 
		if sosa%4 == 0 or sosa%4 == 3 :
			Q00 = sosa*4+2   # grand père paternel
			Q01 = sosa*4+3 # grand mère paternelle
			Q10 = sosa*4+1 # grand mère paternelle
			Q11 = sosa*4   # grand père maternel		
		else :
			Q00 = sosa*4   # grand père paternel
			Q01 = sosa*4+1 # grand mère paternelle
			Q10 = sosa*4+3 # grand mère paternelle
			Q11 = sosa*4+2 # grand père maternel
		
	return [Q00, Q01, Q10, Q11]


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
	Table [i][j]   = sosa*2              # father
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
	DictLines[sosa*2] = [il, jl]         # line to father

	i = basex
	j = basey
	Table [i][j]   = sosa                # sosa
	DictSosa[sosa] = [i, j]

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
	Table [i][j] = sosa*2 + 1            # mother
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
	DictLines[sosa*2+1] = [il, jl]      # line to mother
	
	if n == 3 :
		Sgp = set_grd_parents(mode, HI, sosa)
		i = basex - 1
		j = basey - 1
		Q = Sgp[0]   # top left 00
		Table [i][j] = Q
		DictSosa[Q] = [i, j]
		i = basex + 1
		Q = Sgp[1]   # top right 01
		Table [i][j] = Q
		DictSosa[Q] = [i, j]
		i = basex - 1
		j = basey + 1
		Q = Sgp[2]   # bottom left 10
		Table [i][j] = Q
		DictSosa[Q] = [i, j]
		i = basex + 1
		Q = Sgp[3]   # bottom right 11
		Table [i][j] = Q
		DictSosa[Q] = [i, j]
		return
	
	Sgp = set_grd_parents(mode, HI, sosa)
	Q = Sgp[0]
	x = basex-(t2+1)
	y = basey-(t2+1)
	# top left
	if HI == "I" :
		DictLines[Q] = [x+1, y]
	else :
		DictLines[Q] = [x , y+1]
	DoOneGen (x, y, (size-1)/2, n-2, Q, sens00, mode, 00, HI)   # paternal grand father
	Q = Sgp[1]
	# do h line from father to grand mother
	#DictLines[sosa*4+1] = [basex+1 , basey-(t2+1)]
	# top right
	x = basex+(t2+1)
	y = basey-(t2+1)
	# top left
	if HI == "I" :
		DictLines[Q] = [basex+1 , y]
	else :
		DictLines[Q] = [x , y+1]
	DoOneGen (x, y, (size-1)/2, n-2, Q, sens10, mode, 10, HI)   # paternal grand mother
	Q = Sgp[2]
	# do h line from mother to grand father
	#DictLines[sosa*4+2] = [basex-(t2+1)+1 , basey+(t2+1)]
	# bottom left
	x = basex-(t2+1)
	y = basey+(t2+1)
	# top left
	if HI == "I" :
		DictLines[Q] = [x+1 , y]
	else :
		DictLines[Q] = [x , basey+1]
	DoOneGen (x, y, (size-1)/2, n-2, Q, sens01, mode, 01, HI)   # maternal grand father
	Q = Sgp[3]
	# do h line from mother to grand mother
	#DictLines[sosa*4+3] = [basex+1 , basey+(t2+1)]
	# bottom right
	x = basex+(t2+1)
	y = basey+(t2+1)
	# top left
	if HI == "I" :
		DictLines[Q] = [basex+1 , y]
	else :
		DictLines[Q] = [x , basey+1]
	DoOneGen (basex+(t2+1), basey+(t2+1), (size-1)/2, n-2, Q, sens11, mode, 11, HI)   # maternal grand mother

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
-o : orientation en "H" ("h") (2-1-3 vertical) ou en "I" ("i")(2-1-3 horizontal)(défault)
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
		
if HI == "h" : HI = "H"
if HI == "i" : HI = "I"

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

if Gen%2 == 0 : # skip first and last line
	j = 1
	jl = size-1
else : 
	j = 0
	jl = size
while j < jl :
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
	j += 1

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
	if Gen%2 == 0 : # skip first and last line
		i = 2
		sl = 2**(l-1)-1
	else : 
		i = 1
		sl = 2**(l-1)
	while i <= sl :
		if Idx == "oui" :
			strgx = strgx + str(DictSosa[2**(l-1)-1+i][0]) + "/"
			strgy = strgy + str(DictSosa[2**(l-1)-1+i][1]) + "/"
		else :
			strgx = strgx + str(DictSosa[2**(l-1)-1+i][0]*Dx+Ox) + "/"
			strgy = strgy + str(DictSosa[2**(l-1)-1+i][1]*Dy+Oy) + "/"
		i += 1
	print (strgx)
	print (strgy)
	l += 1

if HI == "I" : O = "0"
else         : O = "1"

strgx = "left%s_%s : /"%(Gen, O)
strgy = "top%s_%s  : /"%(Gen, O)
i = 1
while i < 2**(Gen-(Gen+1)%2) :
	if Gen%2 == 0 :
		strgx = strgx + str(int(DictSosa[i][0]+0.01-1)/2) + "/"
		strgy = strgy + str(DictSosa[i][1]-1) + "/"
	else :
		strgx = strgx + str(DictSosa[i][0]) + "/"
		strgy = strgy + str(DictSosa[i][1]) + "/"
	i += 1
print (strgx)
print (strgy)

DictLines[1] = [0, 0]
strgx = "left%s_%s_ : //"%(Gen, O)
strgy = "top%s_%s_  : //"%(Gen, O)
i = 2
while i < 2**(int(Gen/2)*2-1) :
	if Gen%2 == 0 and i != 1 :
		strgx = strgx + str((DictLines[i][0]-1)/2) + "/"
		strgy = strgy + str(DictLines[i][1]-1) + "/"
	else :
		strgx = strgx + str(DictLines[i][0]) + "/"
		strgy = strgy + str(DictLines[i][1]) + "/"
	i += 1
print (strgx)
print (strgy)
	
print ("Done")


sys.exit(0)


