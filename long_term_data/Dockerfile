FROM python

WORKDIR app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY load_long_term.py .

CMD ["python", "load_long_term.py"]