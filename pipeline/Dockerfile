FROM python

WORKDIR app

COPY requirements.txt

RUN pip install -r requirements.txt

COPY extract.py .

COPY transform.py .

COPY load_short_term.py .

COPY pipeline.py .

CMD ["python", "pipeline.py"]