# snpdb
CropSNPdb code base without /data, /scripts or config files. Uploaded on 19.07.2019.

# Need to create a mysql user with full permissions 
CREATE USER 'flask'@'localhost' IDENTIFIED BY 'CHANGE_ME'; 
# NOTE - we dont want the use to have all privileges in production!!
GRANT ALL PRIVILEGES ON snpdb.* TO 'flask'@'localhost' WITH GRANT OPTION;

# config.py file contains the mySQL access information

# We install flask in a virtual environment, it only worked with --without-pip for me 
sudo python3 -m venv .venv --without-pip
#activate 

# Also the flask package accessing mySQL is incompatible with many python version
# Python 3.7 and installation with pip worked
pip3 install flask
pip3 install Flask-WTF
pip3 install flask-mysqldb
pip3 install pandas
