from escpos.printer import Usb

from configuration.config import settings
from printer.printing import print_lines, cut_docket
from logger.logger import logger


def print_driver_docket(record):
    """
    Prints the driver docket
        Throws an exception if the printer has an error
        record: a record object
    """

    logger.info(f"Printing driver docket: {record}")
    try:
        printer = Usb(
            idVendor=settings.IDVENDOR,
            idProduct=settings.IDPRODUCT,
            in_ep=settings.IN_EP,
            out_ep=settings.OUT_EP,
        )

        # do printer checks

        printer.set(align="center", text_type="B", width=2, height=2)

        printer.text(f"Driver Docket\n")
        printer.text("------------------------\n")

        printer.set(
            align="left",
            font="a",
            text_type="normal",
            width=1,
            height=1,
            density=9,
            invert=False,
            smooth=False,
            flip=False,
        )

        printer.line_spacing(90)
        print_docket_details(printer, record)

        printer._raw(bytes([10]))
        printer.image(settings.LOGO_FILEPATH)
        print_lines(printer, 3)
        cut_docket(printer)

    except Exception as e:
        logger.error(f"FAILED PRINTING DRIVER DOCKET, {e}")
        raise e


def print_plant_docket(record):
    try:
        printer = Usb(idVendor=0x03F0, idProduct=0x0E69, in_ep=0x82, out_ep=0x02)
        printer.set(align="center", text_type="B", width=2, height=2)

        printer.text(f"Plant Docket\n")
        printer.text("------------------------\n")

        printer.set(
            align="left",
            font="a",
            text_type="normal",
            width=1,
            height=1,
            density=9,
            invert=False,
            smooth=False,
            flip=False,
        )

        printer.line_spacing(90)
        print_docket_details(printer, record)

        print_lines(printer, 10)
        printer.image(settings.LOGO_FILEPATH)
        print_lines(printer, 5)

        cut_docket(printer)

    except Exception as e:
        logger.error(f"FAILED PRINTING PLANT DOCKET, {e}")
        raise e


def print_docket_details(printer: Usb, record) -> None:
    """ "Prints the docket details
    Takes a printer object and a record object
    """

    try:
        printer.text(f"Job Number: {record['JobNumber']}\n")
        printer.text(f"Load Time: {record['EndTimeDate']}\n")
        printer.text(f"Unit Weight: {record['UnitWeight']} t\n")
        printer.text(f"Product: {record['product_name']}\n")
        printer.text(f"Customer: {record['customer_name']}\n")
        printer.text(f"Destination: {record['destination_name']}\n")
        printer.text(f"Haulier: {record['haulier_name']}\n")
        printer.text(f"Truck: {record['truck_name']}\n")
        printer.text(f"CA:{record['note']}\n")

        if record["purchaseOrder"]:
            printer.text(f"PO: {record['purchaseOrder']}\n")
    except Exception as e:
        logger.error(f"FAILED PRINTING DOCKET DETAILS, {e}")
        raise e
