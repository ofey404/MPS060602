.. _installation:


==================
Installation Guide
==================

-------------------------
Supported Python Versions
-------------------------

MPS060602 package is developed under python 3.6.

It should work fine with all python version above 3.6.

----------------------------
Installing MPS060602 Package
----------------------------

TODO: pip

Install drivers: 

1. Control panel - device manager - MPS 16bit IEPE
   Data Acquisition - Update Driver.
2. TODO: Install driver attached in MPS060602 package.
3. Check :download:`User Guide V1.0 (Chinese) <_static/MPS-060602UserGuideChineseV1.0.pdf>`
   for more details.

----------------------
Check Acquisition Card
----------------------

A MPS-060602 card and a waveform generator is needed.
If you have an oscilloscope, it would be better.

To be careful, we could test the waveform generator with
a oscilloscope:

.. image:: _static/wave-generator.jpg
    :width: 75%

If we have labview 7.1+ installed, we can use
:download:`MPS-060602 Data Acquisition V2.0.exe <_static/MPS-060602 Data Acquisition V2.0/MPS-060602 Data Acquisition V2.0.exe>`
to ensure our acquisition card working correctly.

:download:`Manual (Chinese) <_static/MPS-060602 Data Acquisition V2.0/MPS-060602 Data Acquisition V2.0 软件使用说明.pdf>`

Wire MPS-060602 and waveform generator together:

.. image:: _static/card-to-wave-generator.jpg
    :width: 75%

And use MPS-060602 Data Acquisition V2.0.exe to observe the waveform:

.. image:: _static/labview-interface.jpg
    :width: 75%