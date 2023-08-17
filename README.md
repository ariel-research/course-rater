# course-rater


## Deploying react and django with nginx and guincorn
#### The following guide is taken from [here](https://austinogiza.medium.com/deploying-react-and-django-rest-framework-with-nginx-and-gunicorn-7a0553459500), but has been adjusted for our app.
### Requirements
#### Tools
1. GitHub.
2. AWS/DigitalOcean/Cloudcone i.e a cloud provider
3. Domain

#### First login to your server using putty and your root access
#### Use terminal and run:
`apt update && apt upgrade -y`

#### Create a limited user and give sudo privileges
run `adduser USERNAME` \
Enter password and skip through the rest of the questions. \
then run adduser `USERNAME sudo` \
logout as root by typing exit and log in with your username: `ssh username@IP` 

#### Install both [frontend](https://github.com/ariel-research/cap-frontend/tree/ariel) and [backend](https://github.com/ariel-research/cap-backend/tree/ariel) 

### Set Up Nginx Server Blocks
Creating the First Server Block File For React Frontend

#### Install Nginx:
`sudo apt install nginx`

### For frontend (but still required for backend):
#### Build the react app (use `npm run build`)
#### As mentioned above, we will create our first server block config file by copying over the default file:
`sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/ariel-courses`

#### Now, open the new file you created in your text editor with sudo privileges:
`sudo nano /etc/nginx/sites-available/ariel-courses`

#### Ignore the commented lines, and look at the code similar to this:

    server {
        listen 80 ;
        listen [::]:80;

       root /home/username/cap/cap-frontend/build;
       index index.html index.htm;

       server_name your_IP domain.com www.domain.com;

        location / {
                try_files $uri /index.html =404;
        }
    }

#### Then Enable the file by linking to the sites-enabled dir
`sudo ln -s /etc/nginx/sites-available/ariel-courses /etc/nginx/sites-enabled`

#### Test NGINX config
`sudo nginx -t`

#### Restart Nginx Server
sudo systemctl restart nginx

### For backend
#### Create the Second Server Block File which will be for django
#### Install some dependencies
run `sudo apt install ufw` 

#### Activate the virtual environment and run the following command in the backend root directory:
`python manage.py collectstatic`

#### Install Gunicorn
run `pip install gunicorn`

#### Check to see if gunicorn can host your django project.
run `gunicorn --bind 0.0.0.0:8000 cap-backend.wsgi`

#### Create gunicorn systemd file
run `sudo nano /etc/systemd/system/gunicorn.service`
#### Paste the following and be sure to update your project name, path and username accordingly:
    [Unit]
    Description=gunicorn daemon
    After=network.target
    [Service]
    User=username
    Group=www-data
    WorkingDirectory=/home/username/cap/cap-backend
    ExecStart=/home/username/cap/cap-backend/venv/bin/gunicorn --access-logfile - --workers 3  cap.wsgi:application --bind <hostname:backend-port>
    WantedBy=multi-user.target

> You can find the logs with this command: `sudo journalctl -f -u gunicorn`

#### Run the following commands to enable gunicorn:
`sudo systemctl start gunicorn` \
`sudo systemctl enable gunicorn` \
`sudo systemctl status gunicorn` \
`sudo systemctl daemon-reload` \
`sudo systemctl restart gunicorn` 

 Now that we have our initial server block configuration, we can use that as a basis for our second file. Copy it over to create a new file:
`sudo cp /etc/nginx/sites-available/ariel-courses /etc/nginx/sites-available/test`

#### Open the new file with sudo privileges in your editor:
`sudo nano /etc/nginx/sites-available/test`

#### Paste the following and be sure update your own IP, username, path and project name
> This covers http, https will be covered below

    server {
        listen 80;
        server_name IP;
        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
            root /home/username/cap/cap-backend;
        }
        location / {
            include proxy_params;
            proxy_pass http://<hostname:backend-port>;
        }
    }

#### Link and test nginx config
Link: `sudo ln -s /etc/nginx/sites-available/cap-backend/etc/nginx/sites-enabled` \
Test: `sudo nginx -t`

#### Reload Nginx and Gunicorn
`sudo systemctl restart gunicorn` \
`sudo systemctl restart nginx`

#### In order to avoid a possible hash bucket memory problem that can arise from adding additional server names, we will also adjust a single value within our `/etc/nginx/nginx.conf file`. Open the file now:
`sudo nano /etc/nginx/nginx.conf`

#### Within the file, find the server_names_hash_bucket_size directive. Remove the # symbol to uncomment the line:

> /etc/nginx/nginx.conf


    http {
        . . .
        server_names_hash_bucket_size 64;
        . . .
    }

