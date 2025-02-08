from kafka import KafkaConsumer
from multiprocessing import Process
from time import sleep
import requests

# definir o ip e a porta do broker


def listen_device_messages():
    print("Listening device messages")
    consumer = KafkaConsumer("device_message", bootstrap_servers="localhost:9092")

    for msg in consumer:
        print("Chegou uma mensagem no topico de mensagens: ", msg.value)
        requests.post("http://localhost:8000/device_message", data=msg.value)


def send_liveness_probe():
    while True:
        sleep(2)
        requests.post("http://localhost:8000/check_liveness_probe")
        print("Checando dispositivos inativos")


if __name__ == "__main__":
    p1 = Process(target=listen_device_messages)
    p2 = Process(target=send_liveness_probe)

    p1.start()
    p2.start()
    p1.join()
    p2.join()
