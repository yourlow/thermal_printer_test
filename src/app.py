import schedule
import time
import json
import os
import redis

from logging.logger import logger
from printer.dockets import print_driver_docket, print_plant_docket
logger.info("Starting Kingscliff Sands Thermal Printer")









def getJobFields(jobDetail, field: str, name: str, backup: str):
    if jobDetail["job"].get(field):
        return jobDetail["job"][field].get(name, jobDetail["job"][backup])
    else:
        return jobDetail["job"][backup]

def getJobDetailFields(jobDetail, field: str, name: str, backup: str) -> str:
    if jobDetail.get(field):
        return jobDetail[field].get(name, jobDetail[backup])
    else:
        return jobDetail[backup]


def check_redis(redis_client):
    try:
        ping = redis_client.ping()
        print(f"Redis client is connected {ping}", flush=True)
    except redis.exceptions.ConnectionError:
        print("Error: Redis client is not connected", flush=True)
        exit(1)



logger.info("Connecting to Redis")

pool = redis.ConnectionPool()

redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True,
                socket_keepalive=True, health_check_interval=10)


check_redis(redis_client)





def print_job(jobs):
    three_dockets_trucks = ["CRD090"]
    two_dockets = ["Tweed Coast Sand & Gravel", "Quintear Pty Ltd", "AJH", "Skykes Haulage", "Holcim"]
    two_dockets_trucks = ["XQ28VM", "XN56UJ", "XO82LW"]


    logger.info(f"Printing JobNumber: {jobs['JobNumber']}")

    #@Todo check each record for errors
    try:
        if(jobs['truck_name'] in three_dockets_trucks):
            logger.info(f"Printing Driver Docket for JobNumber: {jobs['JobNumber']}")
            print_driver_docket(jobs)
            logger.info(f"Printing Driver Docket for JobNumber: {jobs['JobNumber']}")
            print_driver_docket(jobs)
            logger.info(f"Printing Customer Docket for JobNumber: {jobs['JobNumber']}")
            print_plant_docket(jobs)

        elif(jobs['haulier_name'] in two_dockets or jobs['truck_name'] in two_dockets_trucks):
            logger.info(f"Printing Driver Docket for JobNumber: {jobs['JobNumber']}")
            print_driver_docket(jobs)
            logger.info(f"Printing Customer Docket for JobNumber: {jobs['JobNumber']}")
            print_plant_docket(jobs)
        else:
            logger.info(f"Printing Single Docket ${jobs['haulier_name']}, JobNumber: {jobs['JobNumber']}")
            print_plant_docket(jobs)
        jobnumber = jobs['JobNumber']
        logger.info("Finished Printing")


    except:
        logger.error(f"Failed to print JobNumber: {jobs['JobNumber']}")
       

def listen_to_messages(poll_interval=1):
    print(f"Listening for messages on Redis channel: {os.getenv('REDIS_QUEUE')}")
    while True:


        redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True,
                socket_keepalive=True, health_check_interval=10)
        try:
            message = redis_client.rpop("printer")
            if message:
                jobDetail = json.loads(message)
                docketNumber = jobDetail["docketNumber"]
                unitWeight = jobDetail["amount"]

                pickupTime = convert_utc_to_sydney(jobDetail["startTime"])
                customer = getJobFields(jobDetail, "customer", "name", "customerName")
                haulier = getJobFields(jobDetail, "haulier", "name", "haulierName")
                truck = getJobFields(jobDetail, "truck", "rego", "truckName")

                source = getJobDetailFields(jobDetail, "source", "name", "sourceName")
                material = getJobDetailFields(jobDetail, "material", "name", "materialName")
                destination = getJobDetailFields(jobDetail, "destination", "name", "destinationName")

                try:
                    if("topsoil" in material.lower()):
                        return
                except:
                    pass

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
            # check_redis(redis_client)

            redis_client.close()
            time.sleep(poll_interval)
        except Exception as e:
            print(f"Error: {e}", flush=True)
            exit(1)

# Example usage


if __name__== "__main__":
    listen_to_messages()
