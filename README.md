# Vuln-API-App

Vuln-API-app is vulnerable python web application written in flask, bootstrap, HTML, CSS and JavaScript which is inspired from the web APIs that I've found to be vulnerable amomng several Organizations exposing data of thousands of users!

## Deploy and HACK

### Manual Method

- Install [Python](https://python.org) and [git](https://git-scm.com/download)

- Clone Repository

  ```bash
  git clone --depth=1 https://github.com/dmdhrumilmistry/Vulnerable-API-App
  ```

- Change to application directory

  ```bash
  cd Vulnerable-API-App
  ```

- Install Requirements

  ```bash
  python -m pip install -r requirements.txt
  ```

- Start application

  ```bash
  # Using python
  python wsgi.py

  # Using gunicorn (works only on linux distros)
  gunicorn --bind 0.0.0.0:5000 wsgi:app

  # Run in debug mode
  python app.py

  ```

### Hack On TryHackMe

- [Visit Room](https://tryhackme.com/room/vulnerableapiapproom)
- [Room WriteUp](https://dmdhrumilmistry.github.io/blog/blog-ctf/tryhackme/2022/07/13/Vunerable-API-App.html)

## ToDo

- [ ] Create Docker Stable Container
