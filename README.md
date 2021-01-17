

<p align="center">
  <img src="https://i.ibb.co/cJB59D9/android-chrome-512x512.png" alt="MenuCarloLogo" border="0" height="200" width="200">
</p>

MenuCarlo helps F&B owners optimize their menu using their historical transactions data. We make menu engineering and data science techniques accessible to non-technical business owners.

* **Understand Your Business.** Instantly learn about how popular/profitable your menu items are. Find out how your revenue changed over time.
* **Optimize Your Menu.** Learn how you can modify your menu to maximize profits, using custom simulations run for you.
* **Set and Forget.** Connect to your [Square](https://squareup.com/us/en) account after signing up and never worry about importing data. 

## How It Works
MenuCarlo's backend is built using `Django` and `Django Rest Framework`.

1. **Authentication.** JWT auth is handles using `DRF-simpleJWT`. Access tokens expire in 5 minutes, while refresh tokens expire in 24 hours. API routes `/token`, `/token/refresh` and `/token/verify` are used for login, refreshing tokens, and verifying tokens respectively. 
2. **Periodic Tasks.** `Celery` tasks, in conjunction with `django-celery-beat` and `Redis`, automatically extracts new transactions data from Square every 12 hours, then reruns analytics and simulation results after incorporating the new data.
3. **Data Storage.** `PostgreSQL` is our database of choice. Since  historical transactions data needs to be stored and periodically processed, `AWS S3` serves as static file storage. `django-storages` allows us to integrate `S3` into our Django app. 
4. **Hosting.** The backend app itself, along with `PostgreSQL` and `Redis`, are hosted on Heroku's free tier. 

*Check out MenuCarlo's frontend [here](https://github.com/michaelchen-lab/menucarlo-frontend)!*
