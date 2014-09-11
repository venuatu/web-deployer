# web-deployer

A simple way to `git pull && ./deploy.sh` from a webhook  
Open up app.py to see how things work!  

## Installation

This needs mongodb, python and pip and has so far been used on ubuntu

~~~~~sh

# clone this repo
# maybe create a virtualenv
pip install -r requirements.txt
cp config.py.sample config.py

sudo adduser webdeploy
sudo visudo# add: %webdeploy ALL=(ALL) NOPASSWD:/usr/bin/service *

cp upstart.conf /etc/init/web-deployer.conf
sudo service web-deployer start

# maybe expose this via a reverse proxy

mongo reloader <<< "db.sites.insert({_id: '{NAME}', path: '{PATH}'})"
# and allow the webdeploy user access to folder
~~~~~

Then add a web hook to your hosting provider pointing at `http://{HOSTNAME}:5010/push/{SITE}`  
Done!  

If you would like to see the deployment results see `db.deploys.find()` in the mongo shell

## LICENSE

MIT
