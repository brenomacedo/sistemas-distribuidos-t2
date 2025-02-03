from requests import request
from kafka import KafkaConsumer

consumer = KafkaConsumer("device_messages", bootstrap_servers="localhost:9092")

for msg in consumer:
    print("Chegou uma mensagem: ", msg.value)
    request("GET", "http://localhost:8000")
