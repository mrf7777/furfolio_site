# Furfolio
A light-weight and simple commission management website made with Django and HTMX. Intended as a furry-first platform with respect to users and content.

## Why?
A free to use web platform that allows for managing the entire artist's commission lifecycle.
1. Publishing commission openings.
2. Accepting commission requests with automation to manage workload.
3. Tracking commission progress with two-way communication.
4. Completing and archival of commission openings.

Furfolio does not handle payment between buyer and creators and delegates that to the user.

## How?
### Official Site
You can visit [https://www.furfolio.net/](https://www.furfolio.net/)

### Local Hosting
1. Clone this repo
2. Install Python 3.11 or better.
3. Run `python3 -m pip install -r requirements.txt`
4. Run `source dev-vars.sh`
5. Run `python manage.py migrate`
6. Run `python manage.py runserver`
7. Visit [http://localhost:8000/](http://localhost:8000/)
