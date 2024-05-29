import mysql.connector
import schedule
import time
from escpos.printer import Usb
from escpos.constants import PAPER_PART_CUT
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import printer_status
import redis

load_dotenv()

def check_env():
    if os.getenv("REDIS_HOST") is None:
        logging.error("REDIS_HOST not set")
        exit(1)
    if os.getenv("REDIS_PORT") is None:
        logging.error("REDIS_PORT not set")
        exit(1)
    if os.getenv("REDIS_USER") is None:
        logging.error("REDIS_USER not set")
        exit(1)
    if os.getenv("REDIS_PASSWORD") is None:
        logging.error("REDIS_PASSWORD not set")
        exit(1)
    if os.getenv("REDIS_QUEUE") is None:
        logging.error("REDIS_DATABASE not set")
        exit(1)


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', 
                    level=logging.INFO, 
                    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("Starting Kingscliff Sands Thermal Printer")
# Determine the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path
logoImage = os.path.join(script_directory, './logoReduced.jpg')

mysql_connection = None

logging.info("Connecting to Database")

check_env()


r = redis.Redis(host=os.getenv("REDIS_HOST"),
                port=os.getenv("REDIS_PORT"),
                db=0,
                password=os.getenv("REDIS_PASSWORD"),
                decode_responses=True)


sub = r.pubsub("printer")


def validate_message()

for message in sub.listen():
    if message['type'] == 'message':
        
        logging.info(f"Received Message: {message['data']}")
        if message['data'] == "print":
            logging.info("Printing Dockets")
            print_jobs(message['data'])
        else:
            logging.info("Invalid Message")




two_dockets = ["Tweed Coast Sand & Gravel", "Quintear Pty Ltd", "AJH", "Skykes Haulage"]
two_dockets_trucks = ["XQ28VM", "XN56UJ", "XO82LW"]
def print_jobs(jobs):

    # Iterate over each record
    for record in jobs:
        logging.info(f"Printing JobNumber: {record['JobNumber']}")

        #@Todo check each record for errors
        try:
            if(record['haulier_name'] in two_dockets or record['truck_name'] in two_dockets_trucks):
                logging.info(f"Printing Driver Docket for JobNumber: {record['JobNumber']}")
                print_driver_docket(record)
                logging.info(f"Printing Customer Docket for JobNumber: {record['JobNumber']}")
                print_plant_docket(record)
            else:
                logging.info(f"Printing Single Docket ${record['haulier_name']}, JobNumber: {record['JobNumber']}")
                print_plant_docket(record)
            jobnumber = record['JobNumber']
            logging.info("Finished Printing, Updating Database")


        except:
            logging.error(f"Failed to print JobNumber: {record['JobNumber']}")
            continue

       
  

def print_docket_details(printer: Usb, record) -> None:
    """"Prints the docket details
        Takes a printer object and a record object
    """
    printer.text(f"Job Number: {record['JobNumber']}\n")
    printer.text(f"Load Time: {record['EndTimeDate']}\n")
    printer.text(f"Unit Weight: {record['UnitWeight']} t\n")
    printer.text(f"Product: {record['product_name']}\n")
    printer.text(f"Customer: {record['customer_name']}\n")
    printer.text(f"Destination: {record['destination_name']}\n")
    printer.text(f"Haulier: {record['haulier_name']}\n")
    printer.text(f"Truck: {record['truck_name']}\n")
    printer.text(f"CA:{record['note']}\n")


def print_lines(printer: Usb, spacing: int) -> None:
    for i in range(spacing):
        printer._raw(bytes([10]))

def cut_docket(printer: Usb) -> None:
    printer._raw(bytes([29, 86, 1, 19]))


def print_driver_docket(record):
    """
    Prints the driver docket
        Throws an exception if the printer has an error
        record: a record object
    """
    try:
        printer = Usb(idVendor=0x03F0, idProduct=0x0E69, in_ep=0x82, out_ep=0x02)

        #do printer checks

        printer.set(align='center', text_type='B', width=2, height=2)

        printer.text(f"Driver Docket\n")
        printer.text("------------------------\n")

        printer.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False,
            flip=False)
        
        printer.line_spacing(90)
        print_docket_details(printer, record)

        printer._raw(bytes([10]))
        printer.image(logoImage)
        print_lines(printer, 3)
        cut_docket(printer)

    except Exception as e:
        logging.error(f"Failed to print driver docket, {e}")
        raise e

def print_plant_docket(record):
    try:
        printer = Usb(idVendor=0x03F0, idProduct=0x0E69, in_ep=0x82, out_ep=0x02)
        printer.set(align='center', text_type='B', width=2, height=2)

        printer.text(f"Plant Docket\n")
        printer.text("------------------------\n")

        printer.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False,
            flip=False)
        
        printer.line_spacing(90)
        print_docket_details(printer, record)

        print_lines(printer, 10)
        printer.image(logoImage)
        print_lines(printer, 5)

        cut_docket(printer)

    except Exception as e:
        print(e, flush=True)




