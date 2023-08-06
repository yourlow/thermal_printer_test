import mysql.connector
import schedule
import time
from escpos.printer import Usb
from escpos.constants import PAPER_PART_CUT


# Connect to the MySQL database
mysql_connection = mysql.connector.connect(
  host="kingsliff-sands-trucking-database-do-user-8801771-0.b.db.ondigitalocean.com",
  port=25060,
  user="doadmin",
  password="bkoyee0cmuewh3if",
  database="loadmaster_prod"
)

def job():

    # Create a new cursor
    cursor = mysql_connection.cursor(dictionary=True)

    # Query the MySQL database
    cursor.execute(f"""SELECT * FROM `Detailed Records` WHERE printed = 0""")

    # Iterate over each record
    for record in cursor:
        jobnumber = record['JobNumber']
        print_driver_docket(record)
        print_customer_docket(record)

        cursor.execute('UPDATE record SET printed = 1 WHERE JobNumber = %s', (jobnumber,))
        mysql_connection.commit()
    
    cursor.close()

def print_driver_docket(record):
    try:
        printer = Usb(idVendor=0x03F0, idProduct=0x0E69, in_ep=0x82, out_ep=0x02)
        printer.set(align='center', text_type='B', width=2, height=2)

        printer.text(f"Driver Docket\n")
        printer.text("------------------------\n")

        printer.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False,
            flip=False)
        
        printer.line_spacing(90)
        printer.text(f"Job Number: {record['JobNumber']}\n")
        printer.text(f"Load Time: {record['EndTimeDate']}\n")
        printer.text(f"Unit Weight: {record['UnitWeight']} t\n")
        printer.text(f"Product: {record['product_name']}\n")
        printer.text(f"Customer: {record['customer_name']}\n")
        printer.text(f"Destination: {record['destination_name']}\n")
        printer.text(f"Haulier: {record['haulier_name']}\n")
        printer.text(f"Truck: {record['truck_name']}\n")
        printer.text(f"CA:{record['note']}\n")

        printer._raw(bytes([10]))
        printer.image("./logoReduced.jpg")
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([29, 86, 1, 19]))

    except Exception as e:
        print(e, flush=True)


def print_customer_docket(record):
    try:
        printer = Usb(idVendor=0x03F0, idProduct=0x0E69, in_ep=0x82, out_ep=0x02)
        printer.set(align='center', text_type='B', width=2, height=2)

        printer.text(f"Customer Docket\n")
        printer.text("------------------------\n")

        printer.set(align='left', font='a', text_type='normal', width=1, height=1, density=9, invert=False, smooth=False,
            flip=False)
        
        printer.line_spacing(90)
        printer.text(f"Job Number: {record['JobNumber']}\n")
        printer.text(f"Load Time: {record['EndTimeDate']}\n")
        printer.text(f"Unit Weight: {record['UnitWeight']} t\n")
        printer.text(f"Product: {record['product_name']}\n")
        printer.text(f"Customer: {record['customer_name']}\n")
        printer.text(f"Haulier: {record['haulier_name']}\n")
        printer.text(f"Truck: {record['truck_name']}\n")
        printer.text(f"CA:{record['note']}\n")

        printer._raw(bytes([10]))
        printer.image("./logoReduced.jpg")
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([29, 86, 1, 19]))

    except Exception as e:
        print(e, flush=True)

# Define a function to print the docket
def print_docket(record):
    try:
        printer = Usb(idVendor=0x03F0, idProduct=0x0E69, in_ep=0x82, out_ep=0x02)

        printer.text(f"Job Number: {record['JobNumber']}\n")
        printer.text(f"Load Time: {record['EndTimeDate']}\n")
        printer.text(f"Unit Weight: {record['UnitWeight']}\n")
        printer.text(f"Customer: {record['customer_name']}\n")
        printer.text(f"Product: {record['product_name']}\n")
        printer.text(f"Hauiler: {record['haulier_name']}\n")

        printer.text("--------------------------------\n")

        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))

        printer.image("./logoReduced.jpg")
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([29, 86, 1, 19]))

    except Exception as e:
        print(e, flush=True)

# Schedule the job every 10 seconds
schedule.every(1).seconds.do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)


