from kafka import KafkaConsumer
from multiprocessing import Process
import requests
import json

# definir o ip e a porta do broker

def listen_device_messages():
    print('Listening device messages')
    consumer = KafkaConsumer("device_message", bootstrap_servers="localhost:9092")

    for msg in consumer:
        print("Chegou uma mensagem no topico de mensagens: ", msg.value)
        requests.post("http://localhost:8000/device_message", data=msg.value)

def listen_liveness_probes():
    print('Listening liveness probes')
    consumer = KafkaConsumer("liveness_probe", bootstrap_servers="localhost:9092")

    for msg in consumer:
        print("Chegou uma mensagem liveness probes: ", msg.value)
        requests.post("http://localhost:8000/liveness_probe", data=msg.value)

if __name__ == "__main__":
    p1 = Process(target=listen_device_messages)
    p2 = Process(target=listen_liveness_probes)

    p1.start()
    p2.start()
    p1.join()
    p2.join()