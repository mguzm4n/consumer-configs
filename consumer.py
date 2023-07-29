from kafka import KafkaConsumer
from pymongo import MongoClient
from pyspark.conf import SparkConf
import time
import json
import logging

KAFKA_IP = "127.0.0.1"
KAFKA_PORT = "9092"

MAX_WAIT_TIME_IN_SECONDS = 10
BATCH_SIZE = 10

def json_loader_deserializer(v):
    if v is None:
        return

    try:
        return json.loads(v.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        logging.exception('Unable to decode: %s', v)
        return None


def consume(): 
    # Connect to mongo remote db.
    mongo_client = MongoClient("mongodb://distribuidos:Distribuidos1-2023-a-m-r@localhost:27017/?authMechanism=DEFAULT")
    db = mongo_client["eonet"]
    events_collection = db["events"]
    
    # Create the Consumer instance.
    consumer = KafkaConsumer(
        "events",
        bootstrap_servers = [KAFKA_IP + ':' + KAFKA_PORT],
        auto_offset_reset='earliest',
        value_deserializer=json_loader_deserializer
    )
    
    # Start consuming events from events topic.
    events_received = []
    last_time_from_event_received = time.time()
    for message in consumer:
        
        #print("debug")
        print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition, message.offset, message.key, message.value))
        
        events_received.append(message.value)
        elapsed_time_since_last_event = time.time() - last_time_from_event_received

        if len(events_received) > 0 and (len(events_received) == BATCH_SIZE or elapsed_time_since_last_event > MAX_WAIT_TIME_IN_SECONDS):
        
            events_collection.insert_many(events_received)
            events_received = []

        last_time_from_event_received = time.time()

def main():
    # Set Spark configs.
    conf = SparkConf()

    conf.setAppName("Consumer Spark App")  # Set the application name
    conf.setMaster("spark://spark-master:7077")  # Set the Spark master URL

    # Set driver and executor memory
    conf.set("spark.driver.memory", "1G")
    conf.set("spark.executor.memory", "1G")
    
    # consume()

    
if __name__ == "__main__":
    
    main()