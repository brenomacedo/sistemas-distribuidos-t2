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


def listen_liveness_probe():
    print("Listening liveness probe messages")
    consumer = KafkaConsumer("liveness_probe", bootstrap_servers="localhost:9092")

    for msg in consumer:
        print("Chegou uma mensagem no topico de liveness_probe: ", msg.value)
        requests.post("http://localhost:8000/update_liveness_probe", data=msg.value)


def send_liveness_probe_check():
    while True:
        sleep(6)
        requests.post("http://localhost:8000/check_liveness_probe")
        print("Checando dispositivos inativos")


if __name__ == "__main__":
    p1 = Process(target=listen_device_messages)
    p2 = Process(target=listen_liveness_probe)
    p3 = Process(target=send_liveness_probe_check)

    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()
