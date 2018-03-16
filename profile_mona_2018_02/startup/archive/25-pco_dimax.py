print(__file__)

"""support PCO Dimax detector"""


try:
    pco_dimax = MyPcoDetector("PCOIOC2:", name="pco_dimax")
except TimeoutError:
    print("Could not connect to PCOIOC2:pco_dimax - is the IOC off?")
