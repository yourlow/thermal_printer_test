from escpos.printer import Usb



def print_lines(printer: Usb, spacing: int) -> None:
    for i in range(spacing):
        printer._raw(bytes([10]))

def cut_docket(printer: Usb) -> None:
    printer._raw(bytes([29, 86, 1, 19]))



def get_printer_connection() -> Usb:
    pass


def check_printer(printer: Usb):
    pass