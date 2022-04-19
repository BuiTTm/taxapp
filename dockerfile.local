FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
#RUN chmod 777 -R /var/lib/postgresql/data
#RUN chmod 777 -R /tmp
RUN apt-get update && apt-get install -y 
COPY requirements.txt /code/ 
RUN pip install -r requirements.txt 
COPY . /code/
EXPOSE 8000
