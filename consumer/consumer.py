# consumer/consumer.py
import time
import json
import os
import psycopg2
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

def init_db():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "0818"),
        dbname=os.getenv("POSTGRES_DB", "financial_db")
    )
    conn.autocommit = True
    cur = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ecommerce_transactions (
        transaction_id VARCHAR(50) PRIMARY KEY,
        timestamp TIMESTAMP,
        customer_id VARCHAR(50),
        product_category VARCHAR(100),
        product_id VARCHAR(50),
        price NUMERIC,
        quantity INT,
        payment_method VARCHAR(50),
        shipping_country VARCHAR(100),
        shipping_city VARCHAR(100),
        discount_percent NUMERIC,
        shipping_method VARCHAR(50),
        shipping_cost NUMERIC,
        order_total NUMERIC
    );
    """
    cur.execute(create_table_query)
    cur.close()
    return conn

def insert_transaction(conn, tx):
    cur = conn.cursor()
    query = """
        INSERT INTO ecommerce_transactions (
            transaction_id, timestamp, customer_id, product_category,
            product_id, price, quantity, payment_method,
            shipping_country, shipping_city, discount_percent,
            shipping_method, shipping_cost, order_total
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (transaction_id) DO NOTHING;
    """
    cur.execute(query, (
        tx["transaction_id"],
        tx["timestamp"],
        tx["customer_id"],
        tx["product_category"],
        tx["product_id"],
        tx["price"],
        tx["quantity"],
        tx["payment_method"],
        tx["shipping_country"],
        tx["shipping_city"],
        tx["discount_percent"],
        tx["shipping_method"],
        tx["shipping_cost"],
        tx["order_total"]
    ))
    cur.close()
    conn.commit()

def create_consumer():
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(',')
    while True:
        try:
            consumer = KafkaConsumer(
                os.getenv("TRANSACTION_TOPIC", "transactions_topic"),
                bootstrap_servers=kafka_servers,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="ecommerce_group",
                value_deserializer=lambda v: json.loads(v.decode("utf-8"))
            )
            print("Connected to Kafka broker.")
            return consumer
        except NoBrokersAvailable:
            print("No brokers available. Retrying in 5 seconds...")
            time.sleep(5)

def main():
    # Wait for PostgreSQL to be ready
    conn = None
    while not conn:
        try:
            conn = init_db()
            print("Connected to PostgreSQL and table is ready.")
        except Exception as e:
            print(f"DB connection failed, retrying in 5 seconds. Error: {e}")
            time.sleep(5)

    # Create Kafka consumer with retry logic
    consumer = create_consumer()
    print("Kafka consumer is running. Listening on 'transactions_topic'...")

    for message in consumer:
        tx = message.value
        try:
            insert_transaction(conn, tx)
            print(f"Inserted transaction: {tx['transaction_id']}")
        except Exception as e:
            print(f"Error inserting transaction: {e}")

if __name__ == "__main__":
    main()
