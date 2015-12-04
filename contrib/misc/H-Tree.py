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

def set_grd_parents (m, HI, sosa, v) : # pour dernier niveau

	# v vient du nord=0, est=1, sud=2, ouest=3
	# mode 0 = colimaçon, 1 = escalier
	# orientation 0 = H; 1 = I
	# résultat : Qxx ou xx est le quartier (00 haut/gauche, 01, haut/droite, 10 bas/gauche, 11 bas/droit)
	# et sens = sens du quartier
	
	Viens = [
			 [
			  [ # H, colimaçon
			   [[sosa*4+3, sosa*4, sosa*4+2, sosa*4+1], [2, 2, 0, 0], 1],  # nord                                                     # H, colimaçon, nord
			   [[]], 	  # est
			   [[sosa*4+1, sosa*4+3, sosa*4, sosa*4+2], [2, 2, 0, 0], -1],  # sud
			   [[]] # ouest
			  ],   
			   [ # H, escalier
			   [[sosa*4, sosa*4+2, sosa*4+1, sosa*4+3], [2, 2, 0, 0], -1],
			   [[]],
			   [[sosa*4, sosa*4+2, sosa*4+1, sosa*4+3], [2, 2, 0, 0], -1],
			   [[]]
			  ]
			 ],
			 [
			  [ # I, colimaçon
			   [[]],
			   [[sosa*4+2, sosa*4+3, sosa*4+1, sosa*4], [1, 3, 1, 3], 1],
			   [[]],
			   [[sosa*4, sosa*4+1, sosa*4+3, sosa*4+2], [1, 3, 1, 3], -1]
			  ],
			  [ # I, escalier
			   [[]],
			   [[sosa*4, sosa*4+1, sosa*4+2, sosa*4+3], [1, 3, 1, 3], -1],
			   [[]],
			   [[sosa*4, sosa*4+1, sosa*4+2, sosa*4+3], [1, 3, 1, 3], -1]
			  ]
			 ]
			]		
	o=0
	if HI == "I" : o=1
	Q = Viens[o][m][v][0]
	S = Viens[o][m][v][1]
	return (Viens[o][m][v])

def DoOneGen (basex, basey, size, n, sosa, mode, Q, HI, vient) :
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
	t2 = (size-3)/4
	# vient dit d'où on vient :
	# en mode H, d'en haut (0) ou d'en bas (2)
	# en mode I, de droite (1) ou de gauche (3)
	Sgp = set_grd_parents(mode, HI, sosa, vient)

	sens = Sgp[2]
	if HI == "I" :	
		i  = basex
		j  = basey + sens*(t2+1)
		il = i
		jl = basey - t2
	else :
		i  = basex + sens*(t2+1)
		j  = basey
		il = basex - t2
		jl = j
	Table [i][j]   = sosa*2              # father
	DictSosa[sosa*2] = [i, j]
	# lines ignore Escalier/Colimacon
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
	DictSosa[sosa] = [i, j]              # remember that sosa is at i, j 
	if sosa != 1 :
		# draw lines between sosa and where we come from
		# vient should help there
			
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
		j  = basey - sens*(t2+1)
		il = i
		jl = basey+1
	else :
		i  = basex - sens*(t2+1)
		j  = basey
		il = basex+1
		jl = j
	Table [i][j] = sosa*2 + 1            # mother
	DictSosa[sosa*2+1] = [i, j]
	# lines ignore Escalier/Colimacon
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
		i = basex - 1
		j = basey - 1
		Table [i][j] = Sgp[0][0]
		DictSosa[Sgp[0][0]] = [i, j]
		i = basex + 1
		Table [i][j] = Sgp[0][1]
		DictSosa[Sgp[0][1]] = [i, j]
		i = basex - 1
		j = basey + 1
		Table [i][j] = Sgp[0][2]
		DictSosa[Sgp[0][2]] = [i, j]
		i = basex + 1
		Table [i][j] = Sgp[0][3]
		DictSosa[Sgp[0][3]] = [i, j]
		return
	
	x = basex-(t2+1)
	y = basey-(t2+1)
	# lines ignore Escalier/Colimacon
	# top left
	if HI == "I" :
		DictLines[Sgp[0][0]] = [x+1, y]
	else :
		DictLines[Sgp[0][0]] = [x , y+1]
	DoOneGen (x, y, (size-1)/2, n-2, Sgp[0][0], mode, 00, HI, Sgp[1][0])   # paternal grand father
	# top right
	x = basex+(t2+1)
	y = basey-(t2+1)
	# top left
	if HI == "I" :
		DictLines[Sgp[0][1]] = [basex+1 , y]
	else :
		DictLines[Sgp[0][1]] = [x , y+1]
	DoOneGen (x, y, (size-1)/2, n-2, Sgp[0][1], mode, 10, HI, Sgp[1][1])   # paternal grand mother
	# bottom left
	x = basex-(t2+1)
	y = basey+(t2+1)
	# top left
	if HI == "I" :
		DictLines[Sgp[0][2]] = [x+1 , y]
	else :
		DictLines[Sgp[0][2]] = [x , basey+1]
	DoOneGen (x, y, (size-1)/2, n-2, Sgp[0][2], mode, 01, HI, Sgp[1][2])   # maternal grand father
	# bottom right
	x = basex+(t2+1)
	y = basey+(t2+1)
	# top left
	if HI == "I" :
		DictLines[Sgp[0][3]] = [basex+1 , y]
	else :
		DictLines[Sgp[0][3]] = [x , basey+1]
	DoOneGen (x, y, (size-1)/2, n-2, Sgp[0][3], mode, 11, HI, Sgp[1][3])   # maternal grand mother

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

#if HI == "H" : Mode = "e" # pour l'instant !!

if int(Gen) > 16 :
	print ("Plus de 16 générations, pas raisonnable!!")
	sys.exit()

if Mode == "e" : 
	BMode = "escalier"
	Mode = 1
if Mode == "c" : 
	BMode = "colimaçon"
	Mode = 0
	#print ("Le mode colimacon ne fonctionne pas (encore), mais ça viendra!!")
	#sys.exit()

if Gen % 2 == -1 :
	print ("Nombre de générations impaires seulement")
	sys.exit()

i = 0
if Gen % 2 == 0 : i = 1
InitTable (Gen + i)

size = 2**(int(Gen/2)+1)-1
if Gen%2 == 0 :
	H = 2**(int((Gen-2)/2)+1)-1
else :
	H = 2**(int(Gen/2)+1)-1
W = 2**(int(Gen/2)+1)-1

print ('%s-Tree for %s Generations in mode %s orientation "%s"'%(HI, Gen, BMode, HI))

print ('Matrice %s x %s'%(H, W))

if HI == "H" :
	vient = 2
else :
	if Mode == 1 : # escalier
		vient = 1
	else :
		vient = 3

# Start recursion **************	
DoOneGen ((size+1)/2-1, (size+1)/2-1, size, Gen, 1, Mode, -1, HI, vient)

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
	if len(strg) != 0 :
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

if HI == "I" : O = "0"
else         : O = "1"

strgx = "left%s_%s : /"%(Gen, O)
strgy = "top%s_%s  : /"%(Gen, O)
i = 1
while i < 2**Gen :
	if Gen%2 == 0 :
		strgx = strgx + str(int(DictSosa[i][0]+0.01-1)/2) + "/"
	else :
		strgx = strgx + str(DictSosa[i][0]) + "/"
	i += 1

i = 1
while i < 2**Gen :
	if Gen%2 == 0 :
		strgy = strgy + str(DictSosa[i][1]) + "/"
	else :
		strgy = strgy + str(DictSosa[i][1]) + "/"
	i += 1

print (strgx)
print (strgy)

DictLines[1] = [0, 0]
strgx = "left%s_%s_ : //"%(Gen, O)
strgy = "top%s_%s_  : //"%(Gen, O)

i = 2
while i < 2**(Gen-2) :
	if Gen%2 == 0 and i != 1 :
		strgx = strgx + str((DictLines[i][0]-1)/2) + "/"
	else :
		strgx = strgx + str(DictLines[i][0]) + "/"
	i += 1

i = 2
	
while i < 2**(Gen-2) :
	if Gen%2 == 0 and i != 1 :
		strgy = strgy + str(DictLines[i][1]-1) + "/"
	else :
		strgy = strgy + str(DictLines[i][1]) + "/"
	i += 1

print (strgx)
print (strgy)
	
print ("Done")


sys.exit(0)


