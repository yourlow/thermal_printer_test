import mysql.connector
import schedule
import time
from escpos.printer import Usb
from escpos.constants import PAPER_PART_CUT
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
load_dotenv()

def check_env():
    if os.getenv("DB_HOST") is None:
        logging.error("DB_HOST not set")
        exit(1)
    if os.getenv("DB_PORT") is None:
        logging.error("DB_PORT not set")
        exit(1)
    if os.getenv("DB_USER") is None:
        logging.error("DB_USER not set")
        exit(1)
    if os.getenv("DB_PASSWORD") is None:
        logging.error("DB_PASSWORD not set")
        exit(1)
    if os.getenv("DB_DATABASE") is None:
        logging.error("DB_DATABASE not set")
        exit(1)


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', 
                    level=logging.INFO, 
                    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("Starting Printer Service")
# Determine the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path
logoImage = os.path.join(script_directory, './logoReduced.jpg')

mysql_connection = None

logging.info("Connecting to Database")

check_env()



try:
    mysql_connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
    )

except Exception as e: 
    logging.error("Failed to connect to Database")
    exit(1)

if mysql_connection.is_connected():
    logging.info("Connected to Database")

else:
    logging.error("Failed to connect to Database")
    exit()


two_dockets = ["Tweed Coast Sand & Gravel", "Quintear Pty Ltd"]

def job():
    # logging.info("Checking Database")
    mysql_connection.start_transaction(isolation_level='READ COMMITTED')
    # Create a new cursor
    cursor = mysql_connection.cursor(dictionary=True)

    # Query the MySQL database
    cursor.execute(f"""SELECT * FROM `Detailed Records` WHERE printed = 0""")
    rows = cursor.fetchall()
    jobnumbers_to_update = []
    if(len(rows) != 0):
        logging.info(f"Found {len(rows)} record{'s' if len(rows) > 1 else ''} to print")
        # Iterate over each record
        for record in rows:
            logging.info(f"Printing JobNumber: {record['JobNumber']}")

            #@Todo check each record for errors
            try:
                if(record['haulier_name'] in two_dockets):
                    logging.info(f"Printing Driver Docket for JobNumber: {record['JobNumber']}")
                    print_driver_docket(record)
                    logging.info(f"Printing Customer Docket for JobNumber: {record['JobNumber']}")
                    print_plant_docket(record)
                else:
                    logging.info(f"Printing Single Docket ${record['haulier_name']}, JobNumber: {record['JobNumber']}")
                    print_plant_docket(record)
                jobnumber = record['JobNumber']
                logging.info("Finished Printing, Updating Database")

                cursor.execute('UPDATE record SET printed = 1 WHERE JobNumber = %s', (jobnumber,))

            except:
                logging.error(f"Failed to print JobNumber: {record['JobNumber']}")
                continue

       
    mysql_connection.commit()
    cursor.close()


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

        printer._raw(bytes([10]))
        print_lines(printer, 20)
        printer.image(logoImage)
        print_lines(printer, 5)

        cut_docket(printer)

    except Exception as e:
        print(e, flush=True)


logging.info("Starting Scheduler")
# Schedule the job every 10 seconds
schedule.every(10).seconds.do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)


