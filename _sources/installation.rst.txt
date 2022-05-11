.. _installation:

==================
Installation Guide
==================

------------------------------
Manual and Supporting Material
------------------------------

* Manual (Chinese): :download:`MPS-060602 Data Acquisition V2.0 软件使用说明<_static/MPS-060602 Data Acquisition V2.0/MPS-060602 Data Acquisition V2.0 软件使用说明.pdf>`.
* Example applications under `example/ directory <https://github.com/ofey404/MPS060602/tree/main/examples>`_.
* `API Documentation <api/modules>`_.

-------------------------
Supported Python Versions
-------------------------

MPS060602 package is developed under python 3.6, should work fine with all python version above.

----------------------------
Installing MPS060602 Package
----------------------------

This package currently hosted `on test.pypi.org <https://test.pypi.org/project/MPS060602/>`_.

.. code:: bash

    python -m pip install -i https://test.pypi.org/simple/ MPS060602

Driver included, you can quickly find them with following command:

.. code:: python

    import mps060602
    mps060602.core.static_file_path()
    # Like this: WindowsPath('c:/users/.../mps060603/static')

Install drivers 

1. Control panel - device manager - MPS 16bit IEPE
   Data Acquisition - Update Driver.
2. Install the driver under `static/driver` directory.
   Check :download:`User Guide V1.0 (Chinese) <_static/MPS-060602UserGuideChineseV1.0.pdf>`
   if needed.
   

-------------------------
Check Waveform Generator
-------------------------

A MPS-060602 card and a waveform generator is needed.
If you have an oscilloscope, it would be better.

To be careful, we could test the waveform generator with
a oscilloscope:

.. image:: _static/wave-generator.jpg
    :width: 75%

----------------------
Check Acquisition Card
----------------------

If we have labview 7.1+ installed, we can use
:download:`MPS-060602 Data Acquisition V2.0.exe <_static/MPS-060602 Data Acquisition V2.0/MPS-060602 Data Acquisition V2.0.exe>`
to ensure our acquisition card working correctly.

Wire MPS-060602 and waveform generator together:

.. image:: _static/card-to-wave-generator.jpg
    :width: 75%

And use MPS-060602 Data Acquisition V2.0.exe to observe the waveform:

.. image:: _static/labview-interface.jpg
    :width: 75%


-----------------------
Run Example Application
-----------------------

There are some example applications under `example directory <https://github.com/ofey404/MPS060602/tree/main/examples>`_.

* voltmeter.py
* waveform_peeker.py

Read `MPS060602 Tutorial <tutorial>`_ for more information.
