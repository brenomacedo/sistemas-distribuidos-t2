from random import randbytes
from time import sleep, time
from kafka import KafkaProducer
from threading import Thread
from concurrent import futures
import grpc
from proto import grpc_pb2
from proto import grpc_pb2_grpc
import json


class RemoteDeviceServicer(grpc_pb2_grpc.RemoteDeviceServicer):
    def __init__(self, device):
        super()

        self.device = device

    def SendMessage(self, request, context):
        # Lógica para o método SendMessage
        print("Device", self.device.get_short_id(), "Recebou uma mensagem")
        if request.name == "TURN_ON":
            print("Ligando a lampada de id " + self.device.get_short_id())
            self.device.powered_on = True
        elif request.name == "TURN_OFF":
            print("Desligando a lampada de id " + self.device.get_short_id())
            self.device.powered_on = False
        elif request.name == "CHANGE_COLOR":
            print(
                "Mudando a cor da lampada de id "
                + self.device.get_short_id()
                + " para "
                + f"[{request.params[0]}, {request.params[1]}, {request.params[2]}]"
            )
            self.device.color = request.params
        elif request.name == "CHANGE_INTENSITY":
            print(
                "Mudando a intensidade da lampada de id "
                + self.device.get_short_id()
                + " para "
                + f"{request.params[0]}"
            )
            self.device.intensity = request.params[0]

        response = grpc_pb2.MessageResponse(
            success=True,
            message="Mensagem recebida com sucesso",
        )

        return response


class Lamp:
    def __init__(
        self,
        name="Lampada",
        broker_ip="localhost",
        broker_port=9092,
        grpc_listen_port=50000,
        host="localhost",
    ):
        self.run = True
        self.server = None

        self.name = name
        self.type = "LAMP"

        self.powered_on = True
        self.color = [122, 122, 122]
        self.intensity = 50

        self.host = host
        self.grpc_listen_port = grpc_listen_port

        self.broker_ip = broker_ip
        self.broker_port = broker_port

        self.device_id = f"{int(time() * 1000)}-{randbytes(20).hex()}"

        self.producer = KafkaProducer(
            bootstrap_servers=f"{self.broker_ip}:{self.broker_port}",
            value_serializer=lambda x: json.dumps(x).encode(),
        )

    def get_short_id(self):
        return self.device_id[:8]

    def send_status(self):
        try:
            while self.run:
                if self.powered_on:
                    self.producer.send(
                        "device_message",
                        {
                            "device_id": self.device_id,
                            "name": self.name,
                            "device_type": self.type,
                            "message_type": "TEMPERATURE_REPORT",
                            "status": {
                                "powered_on": self.powered_on,
                                "color": self.color,
                                "intensity": self.intensity,
                            },
                            "device_ip": self.host,
                            "device_port": self.grpc_listen_port,
                        },
                    )
                sleep(1)
        except Exception as e:
            print(f"Erro ao enviar status: {e}")

    def send_liveness_probe(self):
        try:
            while self.run:
                self.producer.send(
                    "liveness_probe",
                    {"device_id": self.device_id},
                )
                sleep(4)
        except Exception as e:
            print(f"Erro ao enviar status: {e}")

    def listen_messages(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        grpc_pb2_grpc.add_RemoteDeviceServicer_to_server(
            RemoteDeviceServicer(self), self.server
        )

        # Escutando na porta 50051
        print(f"Servidor gRPC ouvindo na porta {self.grpc_listen_port}...")
        self.server.add_insecure_port(f"[::]:{self.grpc_listen_port}")
        self.server.start()

    def start(self):
        send_status_thread = Thread(target=self.send_status)
        send_status_thread.start()

        listen_messages = Thread(target=self.listen_messages)
        listen_messages.start()

        liveness_probe = Thread(target=self.send_liveness_probe)
        liveness_probe.start()

        input("Pressione Enter para encerrar o dispositivo!\n")
        print("Encerrando o dispositivo")
        self.run = False

        self.server.stop(0)
        listen_messages.join()
        send_status_thread.join()


name = input("Digite o nome do dispositivo: (Ex: Lampada da Sala): ") or "Lampada"

grpc_listen_port = 50000
try:
    grpc_listen_port = int(
        input(
            "Digite a porta que o grpc vai escutar (Geralmente um numero entre 50000 e 60000): "
        )
    )
except Exception:
    pass

Lamp(name=name, grpc_listen_port=grpc_listen_port).start()
