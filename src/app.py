import time
import json
import redis

from apscheduler.schedulers.blocking import BlockingScheduler

from logger.logger import logger
from configuration.config import settings
from printer.dockets import print_driver_docket, print_plant_docket
from printer.printing import get_printer_connection
from utils.timeConversion import convert_utc_to_sydney

def getJobFields(jobDetail, field: str, name: str, backup: str) -> str:
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
        logger.debug(f"Redis client is connected, {ping}")
    except redis.exceptions.ConnectionError:
        logger.error("Error: Redis client is not connected")
        exit(1)

def print_job(job):
    logger.info(f"Printing Docket: {json.dumps(job)}")
    three_dockets_trucks = ["CRD090"]
    two_dockets = [
        "Tweed Coast Sand & Gravel",
        "Quintear Pty Ltd",
        "AJH",
        "Skykes Haulage",
        "Holcim",
    ]
    two_dockets_trucks = ["XQ28VM", "XN56UJ", "XO82LW"]

    logger.info(f"Printing JobNumber: {job['JobNumber']}")

    # @Todo check each record for errors
    try:
        if job["truck_name"] in three_dockets_trucks:
            logger.info(f"Printing Driver Docket for JobNumber: {job['JobNumber']}")
            print_driver_docket(job)
            logger.info(f"Printing Driver Docket for JobNumber: {job['JobNumber']}")
            print_driver_docket(job)
            logger.info(f"Printing Customer Docket for JobNumber: {job['JobNumber']}")
            print_plant_docket(job)

        elif (
            job["haulier_name"] in two_dockets
            or job["truck_name"] in two_dockets_trucks
        ):
            logger.info(f"Printing Driver Docket for JobNumber: {job['JobNumber']}")
            print_driver_docket(job)
            logger.info(f"Printing Customer Docket for JobNumber: {job['JobNumber']}")
            print_plant_docket(job)
        else:
            logger.info(
                f"Printing Single Docket ${job['haulier_name']}, JobNumber: {job['JobNumber']}"
            )
            print_plant_docket(job)
        jobnumber = job["JobNumber"]
        logger.info("Finished Printing")

    except:
        logger.error(f"Failed to print JobNumber: {job['JobNumber']}")


def main():
    logger.info(f"Listening for messages on Redis channel: {settings.REDIS_QUEUE}")

    logger.info("Polling for messages")
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
        socket_keepalive=True,
        health_check_interval=10,
    )

    try:
        get_printer_connection()

        message = redis_client.rpop("printer")
        if message:
            logger.info(f"Received message: {message}")
            jobDetail = json.loads(message)
            docketNumber = jobDetail["docketNumber"]
            unitWeight = jobDetail["amount"]

            pickupTime = convert_utc_to_sydney(jobDetail["startTime"])
            customer = getJobFields(jobDetail, "customer", "name", "customerName")
            haulier = getJobFields(jobDetail, "haulier", "name", "haulierName")
            truck = getJobFields(jobDetail, "truck", "rego", "truckName")

            source = getJobDetailFields(jobDetail, "source", "name", "sourceName")
            material = getJobDetailFields(
                jobDetail, "material", "name", "materialName"
            )
            destination = getJobDetailFields(
                jobDetail, "destination", "name", "destinationName"
            )

            try:
                if "topsoil" in material.lower():
                    return
            except:
                pass

            batchNumber = jobDetail["batchNumber"]

            purchaseOrder = jobDetail.get("purchaseOrder", None)

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
                "purchaseOrder": purchaseOrder,
            }

            print_job(job)
        redis_client.close()
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":

    scheduler = BlockingScheduler()

    scheduler.add_job(main, 'interval', seconds=1, max_instances=1)
    try:
        logger.info("Starting Kingscliff Sands Thermal Printer")
        # Start the scheduler
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        # Shutdown the scheduler on exit
        scheduler.shutdown()
        logger.error("Starting Kingscliff Sands Thermal Printer")
