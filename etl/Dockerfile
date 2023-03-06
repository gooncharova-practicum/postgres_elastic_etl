FROM python:3.9.5

WORKDIR /etl 

COPY ./requirements.txt ./ 

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . ./ 

ENTRYPOINT ["python3", "load_data_to_elastic.py"]