FROM python

WORKDIR app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY dashboard-streamlit.py .

CMD ["streamlit", "run", "dashboard-streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]