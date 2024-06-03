import schedule
import time
import json
from escpos.printer import Usb
from escpos.constants import PAPER_PART_CUT
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import printer_status
import redis
import pytz

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


check_env()




def getJobFields(jobDetail, field: str, name: str, backup: str):
    if jobDetail["job"].get(field):
        return jobDetail["job"][field].get(name, jobDetail["job"][backup])
    else:
        return jobDetail["job"][backup]

def getJobDetailFields(jobDetail, field: str, name: str, backup: str):
    if jobDetail.get(field):
        return jobDetail[field].get(name, jobDetail[backup])
    else:
        return jobDetail[backup]


def check_redis(redis_client):
    try:
        ping = redis_client.ping()
        print(ping)
        print("Redis client is connected")
    except redis.exceptions.ConnectionError:
        print("Error: Redis client is not connected")
        exit(1)

logging.info("Connecting to Redis")
redis_client = redis.Redis(host=os.getenv("REDIS_HOST"),
                port=os.getenv("REDIS_PORT"),
                decode_responses=True)


check_redis(redis_client)





def print_job(jobs):
    two_dockets = ["Tweed Coast Sand & Gravel", "Quintear Pty Ltd", "AJH", "Skykes Haulage"]
    two_dockets_trucks = ["XQ28VM", "XN56UJ", "XO82LW"]


    logging.info(f"Printing JobNumber: {jobs['JobNumber']}")

    #@Todo check each record for errors
    try:
        if(jobs['haulier_name'] in two_dockets or jobs['truck_name'] in two_dockets_trucks):
            logging.info(f"Printing Driver Docket for JobNumber: {jobs['JobNumber']}")
            print_driver_docket(jobs)
            logging.info(f"Printing Customer Docket for JobNumber: {jobs['JobNumber']}")
            print_plant_docket(jobs)
        else:
            logging.info(f"Printing Single Docket ${jobs['haulier_name']}, JobNumber: {jobs['JobNumber']}")
            print_plant_docket(jobs)
        jobnumber = jobs['JobNumber']
        logging.info("Finished Printing")


    except:
        logging.error(f"Failed to print JobNumber: {jobs['JobNumber']}")
       


def convert_utc_to_sydney(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_time = utc_time.replace(tzinfo=pytz.UTC)
    sydney_tz = pytz.timezone('Australia/Sydney')
    sydney_time = utc_time.astimezone(sydney_tz)
    return sydney_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")
       
  

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

    if(record["purchaseOrder"]):
        printer.text(f"PO: {record['purchaseOrder']}\n")


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


def subscribe_to_channel(channel, client):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    return pubsub

def listen_to_messages(pubsub, poll_interval=1):
    print(f"Listening for messages on Redis channel: {os.getenv('REDIS_QUEUE')}")
    while True:
        try:
            
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                jobDetail = json.loads(message['data'])
                docketNumber = jobDetail["docketNumber"]
                unitWeight = jobDetail["amount"]

                pickupTime = convert_utc_to_sydney(jobDetail["startTime"])
                customer = getJobFields(jobDetail, "customer", "name", "customerName")
                haulier = getJobFields(jobDetail, "haulier", "name", "haulierName")
                truck = getJobFields(jobDetail, "truck", "rego", "truckName")

                source = getJobDetailFields(jobDetail, "source", "name", "sourceName")
                material = getJobDetailFields(jobDetail, "material", "name", "materialName")
                destination = getJobDetailFields(jobDetail, "destination", "name", "destinationName")

                batchNumber = jobDetail["batchNumber"]

                purchaseOrder = jobDetail.get("purchaseOrder", None)

                print(purchaseOrder, flush=True)

                # print("Printing")
                # print(f"Job ID: {jobDetail['jobId']}")
                # print(f"Docket Number: {docketNumber}")
                # print(f"Pickup Time: {pickupTime}")
                # print(f"Customer: {customer}")
                # print(f"Haulier: {haulier}")
                # print(f"Truck: {truck}")
                # print(f"Source: {source}")
                # print(f"Material: {material}")
                # print(f"Destination: {destination}")
                # print(f"Batch Number: {batchNumber}")
                # print(f"Purchase Order: {purchaseOrder}")

                job = {
                    "JobNumber": docketNumber,
                    "EndTimeDate": pickupTime,
                    "UnitWeight": unitWeight,
                    "product_name": material,
                    "customer_name": customer,
                    "destination_name": destination,
                    "haulier_name": haulier,
                    "truck_name": truck,
                    "note": batchNumber,
                    "purchaseOrder": purchaseOrder
                }
                # exit()
                print_job(job)
            time.sleep(poll_interval)
            check_redis(redis_client)

        except Exception as e:
            print(f"Error: {e}", flush=True)
            exit(1)
            continue

# Example usage
pubsub = subscribe_to_channel(os.getenv("REDIS_QUEUE"), redis_client)
listen_to_messages(pubsub)
