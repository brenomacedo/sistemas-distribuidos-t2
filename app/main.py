from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from time import sleep
from threading import Thread


class DeviceMessage(BaseModel):
    device_id: str
    device_type: str
    message_type: str
    temperature: int
    device_ip: str
    device_port: int

class LivenessProbe(BaseModel):
    device_id: str


devices = {}

thread_arg = { 'run': True }
def check_liveness_probes(devices, thread_arg):
    while thread_arg['run']:
        print('Checking liveness probes', thread_arg['run'])
        for device_id, device in devices.items():
            if (datetime.now() - device['last_liveness_probe']).seconds > 30:
                del devices[device_id]
        sleep(2)

Thread(target=check_liveness_probes, args=(devices, thread_arg)).start()

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/device_message")
def handle_device_message(message: DeviceMessage):
    if message.device_id not in devices:
        devices[message.device_id] = {
            **message.model_dump(),
            'last_liveness_probe': datetime.now()
        }
    return {"message": "ok"}

@app.post("/liveness_probe")
def handle_liveness_probe(message: LivenessProbe):
    if message.device_id in devices:
        devices[message.device_id]['last_liveness_probe'] = datetime.now()
    return {"message": "ok"}

@app.get("/devices")
def get_devices():
    return devices

# handle on app finish event
@app.on_event("shutdown")
def run():
    print('setei pra false aq')
    thread_arg['run'] = False
    print(thread_arg["run"])