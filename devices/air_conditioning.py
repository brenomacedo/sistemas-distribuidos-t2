from random import randint, randbytes
from time import sleep, time
from kafka import KafkaProducer
from threading import Thread
import json


class AirConditioning:
    def __init__(self, name = "Ar Condicionado", broker_ip = "localhost", broker_port = 9092, grpc_listen_port = 9000, host = "localhost", port = 9000):
        self.run = True

        self.name = "Ar Condicionado 1"
        self.type = "AIR_CONDITIONING"

        self.powered_on = True
        self.temperature = 25

        self.host = host
        self.grpc_listen_port = grpc_listen_port

        self.broker_ip = broker_ip
        self.broker_port = broker_port
 
        self.hash_id = f"{int(time() * 1000)}-{randbytes(20).hex()}"

        self.producer = KafkaProducer(
            bootstrap_servers=f"{self.broker_ip}:{self.broker_port}",
            value_serializer=lambda x: json.dumps(x).encode(),
        )

    def send_status(self):
        try:
            while self.run:
                if self.powered_on:
                    self.producer.send(
                        "device_message",
                        {
                            "device_id": self.hash_id,
                            "device_type": self.type,
                            "message_type": "TEMPERATURE_REPORT",
                            "temperature": randint(
                                self.temperature - 2, self.temperature + 2
                            ),
                            "device_ip": self.host,
                            "device_port": self.grpc_listen_port
                        },
                    )
                sleep(1)
        except Exception as e:
            print(f"Erro ao enviar status: {e}")

    def listen_messages(self):
        while self.run:
            sleep(1)
            print("Listening")

    def liveness_probe(self):
        try:
            while self.run:
                sleep(10)
                self.producer.send(
                    "liveness_probe",
                    {"device_id": self.hash_id},
                )
        except Exception as e:
            print(f"Erro ao enviar status: {e}")

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
