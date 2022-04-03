FROM python:3.8

WORKDIR /opt/app/chatbotDemo

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["/opt/app/chatbotDemo/entrypoint.sh"]
CMD ["0"]
