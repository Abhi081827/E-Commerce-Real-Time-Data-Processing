# data_simulator.py
import os
import time
import json
import random
import logging
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataSimulator")

def get_kafka_producer(bootstrap_servers):
    """
    Continuously attempts to create a KafkaProducer until successful.
    """
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            logger.info("Connected to Kafka successfully.")
            return producer
        except Exception as e:
            logger.error(f"Error creating Kafka producer: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def main():
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name = os.getenv("TRANSACTION_TOPIC", "transactions_topic")
    fake = Faker()

    categories = ["Electronics", "Clothing", "Home & Kitchen", "Beauty", "Books", "Sports"]
    payment_methods = ["Credit Card", "PayPal", "Crypto", "Cash on Delivery", "Debit Card"]
    shipping_methods = ["Standard", "Express", "Overnight"]
    countries_cities = [
        ("USA", "New York"),
        ("USA", "Los Angeles"),
        ("Canada", "Toronto"),
        ("UK", "London"),
        ("Germany", "Berlin"),
        ("India", "Mumbai"),
        ("India", "Delhi"),
        ("Japan", "Tokyo"),
        ("Australia", "Sydney"),
        ("France", "Paris")
    ]
    discount_options = [0, 0, 0, 5, 10, 15]

    # Get a KafkaProducer with a retry loop
    producer = get_kafka_producer(kafka_servers)

    logger.info(f"Data Simulator started. Publishing to topic '{topic_name}' on {kafka_servers}")
    counter = 1
    while True:
        now = datetime.utcnow().isoformat()
        transaction = {
            "transaction_id": f"T{counter:05d}",
            "timestamp": now,
            "customer_id": f"C{random.randint(1, 500):04d}",
            "product_category": random.choice(categories),
            "product_id": f"P{random.randint(1000, 9999)}",
            "price": round(random.uniform(5, 500), 2),
            "quantity": random.randint(1, 5),
            "payment_method": random.choice(payment_methods),
            "shipping_country": random.choice(countries_cities)[0],
            "shipping_city": random.choice(countries_cities)[1],
            "discount_percent": random.choice(discount_options),
            "shipping_method": random.choice(shipping_methods),
            "shipping_cost": round(random.uniform(5, 30), 2)
        }
        subtotal = transaction["price"] * transaction["quantity"]
        discount_amount = round(subtotal * (transaction["discount_percent"] / 100.0), 2)
        transaction["order_total"] = round(subtotal - discount_amount + transaction["shipping_cost"], 2)

        try:
            producer.send(topic_name, transaction)
            logger.info(f"Produced: {transaction}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
        counter += 1
        time.sleep(1)

if __name__ == "__main__":
    main()
