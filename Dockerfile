#THIS IS ERROR: FROM python:alpine3.8, but docker didn't feedback error msg. Sucks.
# see https://github.com/docker-library/official-images/blob/master/library/python
FROM python:3.7.5-slim

COPY requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt

#EXPOSE 5000

CMD ["python", "/app/app.py"]
