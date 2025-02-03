from random import randint, randbytes
from time import sleep, time
from kafka import KafkaProducer
from threading import Thread
import json


class AirConditioning:
    def __init__(self):
        self.run = True

        self.name = "Ar Condicionado 1"
        self.type = "AIR_CONDITIONING"

        self.powered_on = True
        self.temperature = 25

        self.broker_ip = "localhost"
        self.broker_port = 9092
 
        self.grpc_listen_port = 9000
        self.hash_id = f"{int(time() * 1000)}-{randbytes(20).hex()}"

        self.producer = KafkaProducer(
            bootstrap_servers=f"{self.broker_ip}:{self.broker_port}",
            value_serializer=lambda x: json.dumps(x).encode(),
        )

    def send_status(self):
        while self.run:
            if self.powered_on:
                self.producer.send(
                    "device_messages",
                    {
                        "device_id": self.hash_id,
                        "device_type": self.type,
                        "message_type": "TEMPERATURE_REPORT",
                        "temperature": randint(
                            self.temperature - 2, self.temperature + 2
                        ),
                    },
                )
            sleep(1)

    def listen_messages(self):
        while self.run:
            sleep(1)
            print("Listening")

    def liveness_probe(self):
        while self.run:
            sleep(10)
            self.producer.send(
                "devices_messages",
                {"device_id": self.hash_id, "message_type": "LIVENESS_PROBE"},
            )

    def start(self):
        send_status_thread = Thread(target=self.send_status)
        send_status_thread.start()

        listen_messages = Thread(target=self.listen_messages)
        listen_messages.start()

        input("Pressione Enter para encerrar o dispositivo!\n")
        print("Encerrando o dispositivo")
        self.run = False

        listen_messages.join()
        send_status_thread.join()


AirConditioning().start()
