FROM python:3.8

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/
COPY . /usr/src/app/

ADD image_processing.py /server/
ADD static/ /server/

RUN pip install --no-cache-dir -r requirements.txt



EXPOSE 8000

CMD ["python", "image_processing.py"]
