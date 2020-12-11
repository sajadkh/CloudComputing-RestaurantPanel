FROM python:3.7

ADD . /project

WORKDIR /project

RUN pip install -r requirements.txt
RUN python manage.py makemigrations appPanel
RUN python manage.py migrate 
RUN python initializer.py
RUN chmod 777 ./start.sh

EXPOSE 8001

CMD ["./start.sh"]