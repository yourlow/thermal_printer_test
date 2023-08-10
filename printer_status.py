from escpos.printer import Usb
from escpos.constants import PAPER_PART_CUT
from dotenv import load_dotenv
import logging

def check_printer(printer: Usb):
    pass


    is_printer_closed(printer)


def is_cover_closed(printer: Usb):
    """Checks if the printer cover is closed"""
    logging.debug("Checking Cover Status")
    printer.device.write(printer.out_ep, bytes([16, 4, 2]), printer.timeout)
    data = printer.device.read(printer.in_ep, 1, 1000)

    logging.debug("Read Data: ", bytes(data).hex())
    bits = bin(data[0])[2:].zfill(8)
    output = bits[::-1]
    if(output[2] == "1"):
        return True
    else:
        return False
    

def check_paper(printer: Usb)