import signal
import numpy as np
from mps060602 import MPS060602, MPS060602Para, ADChannelMode, PGAAmpRate

""" Example Application - Voltmeter

Simple Cli voltmeter, press ctrl-c to stop.
"""


def main():
    # init
    para = MPS060602Para(
        ADChannel=ADChannelMode.in1,
        ADSampleRate=10000,
        Gain=PGAAmpRate.range_10V,
    )
    card = MPS060602(device_number=0, para=para, buffer_size=2048)
    card.start()
    signal.signal(signal.SIGINT, close(card))

    while True:
        data = card.read_to_volt()

        # preprocess
        average = np.average(data)
        variance = np.var(data)
        standard_deviation = np.std(data)

        print("average {:.2}, variance {:.2}, standard deviation {:.2}".format(average, variance, standard_deviation))

def close(card):
    def handler(signum, frame):
        print("Card closed.")
        card.suspend()
        card.close()
    return handler


if __name__ == "__main__":
    main()
