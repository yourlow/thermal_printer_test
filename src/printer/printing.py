from escpos.printer import Usb

from configuration.config import settings
from logger.logger import logger

def print_lines(printer: Usb, spacing: int) -> None:
    for i in range(spacing):
        printer._raw(bytes([10]))


def cut_docket(printer: Usb) -> None:
    printer._raw(bytes([29, 86, 1, 19]))


def get_printer_connection() -> Usb:
    try:
        
        printer = Usb(
            idVendor=settings.IDVENDOR,
            idProduct=settings.IDPRODUCT,
            in_ep=settings.IN_EP,
            out_ep=settings.OUT_EP,
        )

        check_printer(printer)

        return printer

    except Exception as e:
        logger.error(f"FAILED CONNECTING TO PRINTER, {e}")
        raise e


def check_printer(printer: Usb):

    logger.info("Printer Status")
    printer.device.write(printer.out_ep, bytes([16, 4, 1]), printer.timeout)
    data = printer.device.read(printer.in_ep, 1, 1000)

    logger.debug("Read Data: ", bytes(data).hex())
    bits = bin(data[0])[2:].zfill(8)
    output = bits[::-1]


    if(output[3] == "1"):
        logger.error("Printer is offline")
    else:
        logger.info("Printer is online")
        raise Exception("Printer is offline")


