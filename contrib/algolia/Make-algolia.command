#!/bin/sh

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

### main script starts here ###

# On fait l'hypothése que Gwd a été démarré
# Peut être pourrait on le démarrer directement ici

BIN_DIR="$HOME/Genea/GeneWeb"
VERS=`ls $BIN_DIR/*.gwdversion | sed s/.gwdversion// | sed 's,%,/,'`

LIV_DIR="$HOME/Genea/Livres"
GW_DIR="$VERS/gw"

#update password, appId and apiKey
./My-params.command
PASSWD="name:password"

# SIZE as reported by GeneWeb
BASE="Grimaldi700"
SIZE="167" # grimaldi

#BASE="Chausey"
#SIZE="3790" # chausey

#BASE=HenriT
#SIZE="8827" # henri

# Limit size of chunck to 10Mb by adjusting SIZE and START
START="0"
#SIZE="10"

echo "--- Starting for $BASE, start=$START, size=$SIZE"

# Crées une version fraîche de $BASE.gw (sources au format lisible geneweb)

Python3 ./Algolia.py --password=$PASSWD --base=$BASE --size=$SIZE --index=$START  --password=$PASSWD
check_errs $? "Make-algolia failed"

echo "---Done---"
