BIN_DIR="$HOME/Genea/GeneWeb"
VERS=`ls $BIN_DIR/*.gwdversion | sed s/.gwdversion// | sed 's,%,/,'`
GW_DIR="$VERS/gw"

cd `dirname $0`

# set PASSWD to the appropriate value
PASSWD="name:passwd"
# the PASSSWD line must be replicated in Make-algolia.sh

sed  's/xy:zz/'${PASSWD}'/g' $GW_DIR/etc/algolia/perso-orig.txt > $GW_DIR/etc/algolia/perso.txt

# The lines below up to "---", updated with your own appId and apikey, should be 
# executed after each install of a new distribution
APPID="appId"
APIKEY="apiKey"
sed  's/DummyAppId/'${APPID}'/g' $GW_DIR/etc/algolia_search-orig.txt > $GW_DIR/etc/algolia_tmp.txt
sed  's/DummyApiKey/'${APIKEY}'/g' $GW_DIR/etc/algolia_tmp.txt > $GW_DIR/etc/algolia_search.txt
rm -f $GW_DIR/etc/algolia_tmp.txt
# -------
