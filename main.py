from bluez_peripheral.util import *
import os
import requests
from dotenv import load_dotenv
import asyncio
from bluez_peripheral.agent import NoIoAgent
from bluez_peripheral.advert import Advertisement, AdvertisingIncludes
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
import time


class ToolloLockerService(Service):
    def __init__(self):
        self._some_value = None
        super().__init__("BEEF", True)

    @characteristic("BEF0", CharFlags.READ)
    def my_readonly_characteristic(self, options):
        print('my_readonly_characteristic trigged')
        return bytes("Hello World!", "utf-8")

    @characteristic("BEF1", CharFlags.WRITE).setter
    def my_writeonly_characteristic(self, value, options):
        print('my_writeonly_characteristic trigged')
        self._some_value = value


load_dotenv()


async def main():
    locker = requests.get(
        '{}/{}'.format(os.getenv('BANCKEND_URL'), os.getenv('GET_LOCKER_PATH')))

    lockerDictData = locker.json()['data']

    bus = await get_message_bus()

    service = ToolloLockerService()
    await service.register(bus)

    # An agent is required to handle pairing
    agent = NoIoAgent()
    # This script needs superuser for this to work.
    await agent.register(bus)

    adapter = await Adapter.get_first(bus)

    my_service_ids = ["BEEF"]  # The services that we're advertising.
    my_appearance = 0  # The appearance of my service.
    # See https://specificationrefs.bluetooth.com/assigned-values/Appearance%20Values.pdf
    # Advert should last 60 seconds before ending (assuming other local
    my_timeout = 1
    # services aren't being advertised).
    # Start an advert that will last for 60 seconds.
    advert = Advertisement("toollo-locker-"+str(lockerDictData['id']), my_service_ids,
                           my_appearance, my_timeout)

    print('service started#0')
    cnt = 1
    await advert.register(bus, adapter)
    while True:
        # Handle dbus requests.
        await asyncio.sleep(2)
        print('service started#{}'.format(cnt))
        await advert.register(bus, adapter)
        cnt += 1
    await bus.wait_for_disconnect()

if __name__ == "__main__":

    asyncio.run(main())
