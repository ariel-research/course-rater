## Cheat Sheet

### Systemd Services
- create a system service:
`sudo nano /etc/systemd/system/name.service`

### Nginx 
#### log files
- access log: `sudo tail -f /var/log/nginx/access.log`
- error log: `sudo tail -f /var/log/nginx/error.log`
#### configuration files
- frontend: `sudo nano /etc/nginx/sites-available/ariel-courses`
- backend: `sudo nano /etc/nginx/sites-available/test`
  
### Gunicorn 
#### log file
- `sudo journalctl -f -u gunicorn`
