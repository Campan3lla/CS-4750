# Office Hour Management System 
##### _Created by Jonah Kim, Tammy Ngo, and Yuxi Yang_

## Website Urls: 
Online Heroku: https://office-hour-manager-7006b16d76d2.herokuapp.com/ \
Offline Local: http://127.0.0.1:8000/

## Running:
1. Clone repository
2. Open a command prompt
3. Install python libraries from requirements.txt: `pip install -r requirements.txt`
4. Run: `python manage.py migrate`
5. Run: `python manage.py runserver`
6. The terminal should provide a URL for accessing the website. 

## Populating Initial Data:
* On the local server, access the url: http://127.0.0.1:8000/test/populate.
* On the online server, the initial data has already been populated.

## Accessing Test Accounts:
* All accounts have the password '123'
* Some example users you can log in as are 'admin' and 'na4thd'
* For a complete listing, you can look at the _data.json_ file within the root of the repository.