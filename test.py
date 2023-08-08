import usb.core
import usb.util
from escpos.printer import Usb
# Initialize printer
printer = Usb(idVendor=0x03F0, idProduct=0x0E69, in_ep=0x82, out_ep=0x02)


def printer_status():
    print("Printer Status")
    printer.device.write(printer.out_ep, bytes([16, 4, 1]), printer.timeout)
    data = printer.device.read(printer.in_ep, 1, 1000)

    print("Read Data: ", bytes(data).hex())
    bits = bin(data[0])[2:].zfill(8)
    output = bits[::-1]
    print("Drawer is", "open" if output[3] == "1" else "closed")
    print("Printer is", "offline" if output[3] == "1" else "online")

def offline_status():
    print("Offline Status")
    printer.device.write(printer.out_ep, bytes([16, 4, 2]), printer.timeout)
    data = printer.device.read(printer.in_ep, 1, 1000)

    print("Read Data: ", bytes(data).hex())
    bits = bin(data[0])[2:].zfill(8)
    output = bits[::-1]
    print("Paper is", "end" if output[3] == "1" else "not end")
    
    print("Error Status:", "error" if output[6] == "1" else "no error")


def paper_sensor_status():
    print("Paper Status")
    printer.device.write(printer.out_ep, bytes([16, 4, 4]), printer.timeout)
    data = printer.device.read(printer.in_ep, 1, 1000)

    print("Read Data: ", bytes(data).hex())
    bits = bin(data[0])[2:].zfill(8)
    output = bits[::-1]    
    print("Is Paper near end:", "yes" if output[6] == "1" else "no")


try:
   printer_status()
   print()
   offline_status()
   print()
   paper_sensor_status()
   

except Exception as e:
    print(e)
