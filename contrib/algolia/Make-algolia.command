#!/bin/bash

check_errs()
{
  # Function. Parameter 1 is the return code
  # Para. 2 is text to display on failure.
  if [ "${1}" -ne "0" ]; then
    echo "ERROR # ${1} : ${2}"
    # as a bonus, make our script exit with the right error code.
    exit ${1}
  fi
}

cd `dirname $0`
HOST=`hostname`

### main script starts here ###

# On fait l'hypothése que Gwd a été démarré
# Peut être pourrait on le démarrer directement ici

#update password, appId and apiKey
if [ "$HOST" == "iMac-H" ]; then
  BIN_DIR="$HOME/Genea/GeneWeb"
  VERS="GeneWeb-7.0a-Mac"
  GW_DIR="$BIN_DIR/$VERS/gw"
  GW_DIRA="$GW_DIR/etc/algolia"
  export BASE_DIR="$HOME/Genea/GeneWeb-Bases"
else
  BIN_DIR="$HOME/geneweb/demo.geneweb.tuxfamily.org-web/htdocs"
  VERS="gw7"
  GW_DIR="$BIN_DIR/$VERS/gw"
  P_DIR="$BIN_DIR/$VERS/algolia"
  export BASE_DIR="$HOME/geneweb/demo.geneweb.tuxfamily.org-web/htdocs/gw7/bases"
fi

# SIZE as reported by GeneWeb

BASE="Grimaldi700"
#BASE="Chausey"
#BASE=HenriT

if [ "${1}" == "" ]; then
  START="0"
else
  START="$1"
fi
if [ "${2}" == "" ]; then
  SIZE="167" # grimaldi
  #SIZE="3790" # chausey
  #SIZE="8827" # henri
else
  SIZE="$2"
fi

#START=2600
#SIZE=10
# Limit size of chunck to 10Mb by adjusting SIZE and START
CHUNK="$3"

echo "--- Starting for $BASE, start=$START, size=$SIZE, chunk=$CHUNK"

python3 --version

python3 ./Algolia.py --base=$BASE --size=$SIZE --index=$START --chunk=$CHUNK
check_errs $? "Make-algolia failed"

echo "---Done---"
