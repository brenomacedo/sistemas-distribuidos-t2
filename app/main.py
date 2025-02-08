from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import grpc
from proto import grpc_pb2
from proto import grpc_pb2_grpc
from fastapi import HTTPException
from pydantic import Field


class DeviceMessage(BaseModel):
    name: str
    device_id: str
    device_type: str
    message_type: str
    temperature: int
    device_ip: str
    device_port: int


class LivenessProbe(BaseModel):
    device_id: str


class ControlDeviceMessage(BaseModel):
    device_id: str
    name: str
    params: list[str] = Field(default=[])
    values: list[int] = Field(default=[])


devices = {}

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/device_message")
def handle_device_message(message: DeviceMessage):
    print(f"Dispositivo de id {message.device_id} mandou uma mensagem")
    devices[message.device_id] = {
        **message.model_dump(),
        "last_liveness_probe": datetime.now(),
    }
    return {"message": "ok"}


@app.get("/devices")
def get_devices():
    return devices


@app.post("/check_liveness_probe")
def check_liveness_probe():
    for key, device in devices.copy().items():
        if device["last_liveness_probe"] < (datetime.now() - timedelta(seconds=5)):
            print(device["last_liveness_probe"])
            print((datetime.now() - timedelta(seconds=5)))
            print(f"Dispositivo de id {key} esta inativo, removendo...")
            del devices[key]


@app.post("/control_device")
def control_device(config: ControlDeviceMessage):
    if config.device_id not in devices:
        raise HTTPException(404, {"message": "Dispositivo Não existe!"})

    device = devices[config.device_id]

    channel = grpc.insecure_channel(f"{device['device_ip']}:{device['device_port']}")
    stub = grpc_pb2_grpc.RemoteDeviceStub(channel)

    message = grpc_pb2.Message(
        name=config.name, params=config.params, values=config.values
    )
    stub.SendMessage(message)
    return {"message": "ok"}
