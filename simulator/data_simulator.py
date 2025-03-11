# simulator/data_simulator.py
import os
import time
import json
import random
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

def create_producer():
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(',')
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=kafka_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("Connected to Kafka broker.")
            return producer
        except NoBrokersAvailable:
            print("No brokers available. Retrying in 5 seconds...")
            time.sleep(5)

def main():
    topic_name = os.getenv("TRANSACTION_TOPIC", "transactions_topic")
    fake = Faker()

    # Sample values for e-commerce data
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

    # Create Kafka Producer with retry logic
    producer = create_producer()

    print(f"Data Simulator started. Publishing to topic '{topic_name}'...")
    counter = 1
    while True:
        now = datetime.utcnow().isoformat()
        transaction_id = f"T{counter:05d}"
        counter += 1

        customer_id = f"C{random.randint(1, 500):04d}"
        category = random.choice(categories)
        product_id = f"P{random.randint(1000, 9999)}"
        price = round(random.uniform(5, 500), 2)
        quantity = random.randint(1, 5)
        payment_method = random.choice(payment_methods)
        country, city = random.choice(countries_cities)
        discount_percent = random.choice(discount_options)
        ship_method = random.choice(shipping_methods)

        if ship_method == "Standard":
            shipping_cost = round(random.uniform(5, 10), 2)
        elif ship_method == "Express":
            shipping_cost = round(random.uniform(10, 20), 2)
        else:  # Overnight
            shipping_cost = round(random.uniform(20, 30), 2)

        subtotal = price * quantity
        discount_amount = round(subtotal * (discount_percent / 100.0), 2)
        order_total = round(subtotal - discount_amount + shipping_cost, 2)

        transaction = {
            "transaction_id": transaction_id,
            "timestamp": now,
            "customer_id": customer_id,
            "product_category": category,
            "product_id": product_id,
            "price": price,
            "quantity": quantity,
            "payment_method": payment_method,
            "shipping_country": country,
            "shipping_city": city,
            "discount_percent": discount_percent,
            "shipping_method": ship_method,
            "shipping_cost": shipping_cost,
            "order_total": order_total
        }

        producer.send(topic_name, transaction)
        print(f"Produced: {transaction}")
        time.sleep(1)

if __name__ == "__main__":
    main()
