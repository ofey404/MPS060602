import time
from codetiming import Timer
import signal
import asyncio
from mps060602 import MPS060602, MPS060602Para, ADChannelMode, PGAAmpRate


def close_card(card):
    card.suspend()
    card.close()


def new_card():
    para = MPS060602Para(
        ADChannel=ADChannelMode.in1,
        ADSampleRate=1000,
        Gain=PGAAmpRate.range_10V,
    )
    card = MPS060602(device_number=0, para=para, buffer_size=2048)
    card.start()
    return card




async def async_read_to_volt(card: MPS060602):
    async def sleep():
        await asyncio.sleep(1)

    async def read_to_volt(card: MPS060602):
        await card.read_to_volt()

    with Timer(text="\n asynchorounous `sleep(1); read_to_volt()` elapsed time: {:.1f}"):
        tasks = [sleep(), read_to_volt(card)]
        await asyncio.gather(*tasks)

def sync_read_to_volt(card: MPS060602):
    with Timer(text="\n synchrounous `sleep(1); read_to_volt()` elapsed time: {:.1f}"):
        time.sleep(1)
        card.read_to_volt()


async def main():
    card = new_card()
    sync_read_to_volt(card)
    await async_read_to_volt(card)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
