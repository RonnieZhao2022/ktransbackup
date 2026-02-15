ls
cd mysite
ls
sqlite
sqlite3
ls
mkdir test_db
cp KTRANS.db test_db/
cd test_db/
vi sqlite3-to-mysql.sh
sqlite3 KTRANS.db .dump > sqlite.sql && bash sqlite3-to-mysql.sh sqlite.sql > mysql.sql && rm sqlite.sql
ls
mysql -u KTRANS -p ktrans < mysql.sql 
mysql
service mysql restart
ls
sqlite3 KTRANS.db .dump > sqlite.sql && bash sqlite3-to-mysql.sh sqlite.sql > mysql.sql && rm sqlite.sql
ls
cd mysite
ls
mkdir test
pip install flask-sqlacodegen
pip install SQLAlchemy==1.4.47
