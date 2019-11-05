#THIS IS ERROR: FROM python:alpine3.8, but docker didn't feedback error msg. Sucks.
# see https://github.com/docker-library/official-images/blob/master/library/python
FROM python:3.7.5-slim


RUN python3 -m pip install Flask
RUN python3 -m pip install requests
RUN python3 -m pip install libra-client
RUN python3 -m pip install waitress

#EXPOSE 5000

CMD ["python", "/app/app.py"]
