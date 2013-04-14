# Assuming you have a fresh couchdb, this will add
# the hammock user and initialize hammock's database
USER="ixle"
PASSWD="ixlee"
HOST="http://127.0.0.1:5999"
DB_NAME="ixle"
#curl -X PUT $HOST/database
#curl -X PUT $HOST/_config/admins/$USER -d '"$PASSWD"'
AUTH_HOST="http://$USER:$PASSWD@127.0.0.1:5984"
curl -X PUT $AUTH_HOST/$DB_NAME
