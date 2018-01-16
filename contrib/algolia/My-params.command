#!/bin/bash

HOST=`hostname`
echo "Host= $HOST"

# These values need to be adjusted to your environment
if [ "$HOST" == "iMac-H" ]; then
  BIN_DIR="$HOME/Genea/GeneWeb"
  VERS="GeneWeb-7.0a-Mac"
  GW_DIR="$BIN_DIR/$VERS/gw"
  P_DIR="$GW_DIR/etc/algolia"
  A_DIR="$HOME/GitHub/a2line/geneweb/hd/etc"
  # set PASSWD to the appropriate value
  PASSWD="xy:zz"
else
  BIN_DIR="$HOME/geneweb/demo.geneweb.tuxfamily.org-web/htdocs"
  VERS="gw7"
  GW_DIR="$BIN_DIR/$VERS/gw"
  P_DIR="$BIN_DIR/$VERS/algolia"
  A_DIR="$BIN_DIR/$VERS/algolia"
  PASSWD="wizard:wizard"
fi
# the PASSSWD line must be replicated in Make-algolia.sh

cd `dirname $0`

sed  's/xy:zz/'${PASSWD}'/g' $P_DIR/perso-orig.txt > $GW_DIR/etc/algolia/perso.tmp
sed  's/xy:zz/'${PASSWD}'/g' $GW_DIR/etc/algolia/perso.tmp > $GW_DIR/etc/algolia/perso.txt
rm $GW_DIR/etc/algolia/perso.tmp

# The lines below up to "---", updated with your own appId and apikey, should be 
# executed after each install of a new distribution
APPID="appId"
APIKEY="apiKey"
sed  's/DummyAppId/'${APPID}'/g' $A_DIR/algolia_search-orig.txt > $GW_DIR/etc/algolia_tmp.txt
sed  's/DummyApiKey/'${APIKEY}'/g' $GW_DIR/etc/algolia_tmp.txt > $GW_DIR/etc/algolia_search.txt
rm -f $GW_DIR/etc/algolia_tmp.txt
# -------
