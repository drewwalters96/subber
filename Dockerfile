FROM python:3

WORKDIR /subber
ADD . /subber

RUN pip3 install -r requirements.txt
RUN pip3 install .

EXPOSE 8000

CMD ["gunicorn", "-b 0.0.0.0", "subber.subber:app", "-t 900"]
