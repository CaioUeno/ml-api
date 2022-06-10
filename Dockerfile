FROM python:3.8

WORKDIR /usr/src/app

# copy files to the container
COPY ./api ./api
COPY ./core ./core
COPY ./db ./db
COPY ./ml ./ml
COPY api.cfg api.cfg
COPY logging.conf logging.conf
COPY main.py main.py
COPY requirements.txt requirements.txt
COPY mnb.sav mnb.sav

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# create log folder
RUN mkdir -p /usr/src/app/logs

# run the command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
