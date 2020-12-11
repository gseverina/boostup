#1 - levantar el compose con la base de datos...
docker-compose up -d

#2 - levantar el virtualenv 
source venv/bin/activate

#3 - crear la base de datos...
cd django_project
python manage.py makemigrations boostup_app
python manage.py migrate boostup_app

#4 - levantar la app...
python manage.py runserver 8080

#5 - ejecutar desde el browser...
http://localhost:8080/oauth/authorize

