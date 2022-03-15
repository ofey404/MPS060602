import matplotlib.pyplot as plt
import time
from mps060602 import MPS060602, MPS060602Para, ADChannelMode, PGAAmpRate

""" Example Application - Waveform Peeker

    Visualize waveform in `buffer_size/sample_rate` seconds.
    Use Channel In1 and range 10 volt.
"""


def main(buffer_size, sample_rate):
    # init
    para = MPS060602Para(
        ADChannel=ADChannelMode.in1,
        ADSampleRate=sample_rate,
        Gain=PGAAmpRate.range_10V,
    )
    card = MPS060602(device_number=0, para=para, buffer_size=buffer_size)
    card.start()

    # read data
    start = time.time()
    buffer = card.data_in()
    diff = time.time() - start
    print(
        "read {} data in {} second, sample rate {} per second".format(
            buffer_size, diff, sample_rate
        )
    )

    # preprocess
    x = [i / sample_rate for i in range(len(buffer))]
    y = list(map(card.to_volt, buffer))

    plt.plot(x, y)
    plt.title(
        "Waveform in {} second\n".format(buffer_size / sample_rate)
        + "Sample rate {}, buffer size {}".format(sample_rate, buffer_size)
    )
    plt.xlabel("time / s")
    plt.ylabel("voltage / V")
    plt.show()

    # handle aftermath
    card.suspend()
    card.close()


if __name__ == "__main__":
    buffer_size = 2048
    sample_rate = 10000
    main(buffer_size, sample_rate)
