"""
    Setup file for MPS060602.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.1.5.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup
from sys import platform

if __name__ == "__main__":
    try:
        if platform != "win32":
            print(
                "\n\nMPS-060602 acquisition card only support windows,",
                "but platform is {}.".format(platform),
            )
            raise
        setup(
            use_scm_version={"version_scheme": "no-guess-dev"},
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
