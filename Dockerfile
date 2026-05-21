#
FROM python:3.10

# setting workdir
WORKDIR /code

# Copying Pipfile.lock file
COPY ./Pipfile.lock /code/Pipfile.lock

RUN  apt-get -y update
RUN  apt-get -y upgrade
RUN apt-get -y install jq
# Generate requirements.tex from Pipefile.lock
RUN jq -r '.default | to_entries[] | .key + .value.version' \
    Pipfile.lock > requirements.txt


#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN  apt-get -y update
RUN  apt-get -y upgrade
#
COPY . /code

#
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]