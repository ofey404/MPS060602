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


def sync_read_to_volt(card: MPS060602):
    with Timer(text="\n synchrounous `sleep(1); read_to_volt()` elapsed time: {:.1f}"):
        time.sleep(1)
        card.read_to_volt()


async def main(loop):
    card = new_card()
    sync_read_to_volt(card)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
