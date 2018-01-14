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

#grep "^${1}:" /etc/passwd > /dev/null 2>&1
#check_errs $? "User ${1} not found in /etc/passwd"

# On fait l'hypothése que Gwd a été démarré
# Peut être pourrait on le démarrer directement ici

VERS="$HOME/Genea/GeneWeb/GeneWeb-6.08-Mac"
BASE_DIR="$HOME/Genea/GeneWeb-Bases"
BIN_DIR="$HOME/Genea/GeneWeb"
VERS=`ls $BIN_DIR/*.gwdversion | sed s/.gwdversion// | sed 's,%,/,'`

LIV_DIR="$HOME/Genea/Livres"
GW_DIR="$VERS/gw"

PYTH_DIR="."

# set PASSWD to the appropriate value
PASSWD="name:passwd"
sed  's/xy:zz/'${PASSWD}'/g' $GW_DIR/etc/algolia/perso-orig.txt > $GW_DIR/etc/algolia/perso.txt

# The lines below up to "---", updated with your own appId and apikey, should be 
# executed after each install of a new distribution
APPID="appId"
APIKEY="apiKey"
sed  's/DummyAppId/'${APPID}'/g' $GW_DIR/etc/algolia_search-orig.txt > $GW_DIR/etc/algolia_tmp.txt
sed  's/DummyApiKey/'${APIKEY}'/g' $GW_DIR/etc/algolia_tmp.txt > $GW_DIR/etc/algolia_search.txt
rm -f $GW_DIR/etc/algolia_tmp.txt
# -------

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


Python3 $PYTH_DIR/Algolia.py --password=$PASSWD --base=$BASE --size=$SIZE --index=$START
check_errs $? "Make-algolia failed"

