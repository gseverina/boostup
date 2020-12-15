#1 - run docker-compose with mongo and mongo-express:
`docker-compose up -d`

#2 - activate virtualenv: 
`source venv/bin/activate`

#3 - setup databse:
`cd django_project`

`python manage.py migrate boostup_app`

#4 - run the web service:
`python manage.py runserver 8080`

#5 - execute the flow from a browser:
`http://localhost:8080/oauth/authorize`
