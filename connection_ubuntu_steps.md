ssh -i "C:\Users\LENOVO\Downloads\ssh.pem" ubuntu@52.91.215.27

sudo apt update && sudo apt upgrade -y

sudo apt install python3-pip
sudo apt install python3-venv python3-full -y
sudo apt install postgresql postgresql-contrib -y

sudo cat /etc/passwd
sudo -i -u postgres

psql -U postgres   --- query tool
\q

cd /etc/postgresql/18/main
ls
sudo vi postgresql.conf
sudo nano /etc/postgresql/18/main/postgresql.conf              ---- mainly used to configure addresses and modes
Below connection settings put  listen_addresses = '*'
then ctrl c and then :wq

sudo nano /etc/postgresql/18/main/pg_hba.conf
change peer to scram-sha 256                                         --- peer is for same system, so we change
make ipv6 address ::/0
ctrl o  enter ctrl x
sudo systemctl restart postgresql
, keep peer only sudo -u postgres psql, and then run ALTER USER postgres WITH PASSWORD 'admin123';, then restart then change and do stuff
then 
psql -U postgres 
\q or exit to come out

host    all    all    223.187.126.148/32    scram-sha-256, add this at end too

security grp should have postgres sql customer my ip and ssh inbound rules and nginx and https-443


cd /home/ubuntu
mkdir app
python3 -m venv venv
source venv/bin/activate
ls -la
deactivate -- to get out use it
mkdir src 
cd src
git clone https://github.com/Abishekvit/FASTAPI.git .
sudo apt update
sudo apt install libpq-dev python3-dev build-essential -y
go to app, then enabe venv then go to src then rn
pip install -r requirements.txt
                                                            ---clone stuff
uvicorn app.main:app
cd ~
touch .env
nano .env, put all variables save
go to .profile add below
set -a
source ~/.env
set +a                                  to automatically get stuff out of env during startup

alembic upgrade head, go to src and do 
uvicorn --host 0.0.0.0 app.main:app
basically means allow anyone, and then go to ip and check
pip install gunicorn : process manager
pip install httptools
pip install uvtools
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000         -- 4 workers of uvicorn
it brings 4 workers

ps -aef | rep -i gunicorn
to test

we need to create a service so that server starts on its own

go to /etc/system/system
sudo nano api.service, paste
systemctl start api
systemctl status api
our system file doesnt have access to env,, so we gave it access

sudo systemctl enable api, to keep it reboot when we start ubuntu

we are going to do HTTPS --- NGINX http GUNICORN(workers)
SSL termination: Handles HTTPS encryption and decryption using an SSL/TLS certificate. Gunicorn receives ordinary HTTP traffic locally.
It fetches the SSL certificate and public key which is sent to browser, browser then sends its key encrypted using public key, which nginx decodes using provate key , and further on they talk using that encypted key
Reverse proxy: Forwards incoming requests to Gunicorn running on port 8000.
Load balancing: Can distribute incoming requests across multiple application servers or workers.

-------------------------------------
user request to port 80(http): when no port specified then http
then nginx asks certbot, certbot issues certificate from lets encrypt
lets encrypt sends a token to server, it sees if server nginx gives the same token so that browser and server are same
then it adds https port on nginx and redrects http request to https 443, 
443 req comes on nginx and it send plan http

------------------------------------
sudo apt install nginx -y
systemctl start nginx
sudo nano /etc/nginx/sites-available/default
it actually worked, can you work it through waht ahppened, i sent a request, nginx accessed and forwarded to port 8000, but incoming rules allow on 80 only, so it allowed from 80 to 8000 to guvicorn

sudo snap install --classic certbot
sudo certbot --nginx
now only ip address is enough after nginx
sudo certbot --nginx -d abishek.webhop.me
go to wifif dns settings and do 8.8.8.8 and 8.8.4.4 to work
check nginx file once
sudo systemctl enable nginx