# consumer.py
import os
import time
import json
import logging
import psycopg2
from kafka import KafkaConsumer, errors
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Consumer")

def init_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            dbname=os.getenv("POSTGRES_DB", "financial_db")
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
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
        """)
        cur.close()
        return conn
    except Exception as e:
        logger.error(f"DB connection failed: {e}")
        raise

def insert_transaction(conn, tx):
    try:
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
        logger.info(f"Inserted transaction: {tx['transaction_id']}")
    except Exception as e:
        logger.error(f"Error inserting transaction {tx['transaction_id']}: {e}")

def wait_for_kafka(bootstrap_servers, topic, retries=10, delay=5):
    """
    Wait until Kafka broker is available by attempting to create a temporary consumer.
    """
    for i in range(retries):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=[bootstrap_servers],
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="test_group",
                value_deserializer=lambda v: json.loads(v.decode("utf-8"))
            )
            consumer.close()
            logger.info("Kafka broker is available.")
            return
        except errors.NoBrokersAvailable:
            logger.warning(f"No Kafka brokers available, retrying in {delay} seconds... (Attempt {i+1}/{retries})")
            time.sleep(delay)
    raise Exception("Kafka broker not available after several retries.")

def main():
    # Initialize DB connection and table
    conn = None
    while not conn:
        try:
            conn = init_db()
            logger.info("Connected to PostgreSQL and table is ready.")
        except Exception as e:
            logger.error(f"DB connection failed, retrying in 5 seconds. Error: {e}")
            time.sleep(5)
    
    # Get Kafka configuration from environment
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("TRANSACTION_TOPIC", "transactions_topic")
    
    # Wait for Kafka broker to be available
    wait_for_kafka(kafka_bootstrap, topic)
    
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[kafka_bootstrap],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="ecommerce_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
    logger.info("Kafka consumer is running. Listening on 'transactions_topic'...")
    
    for message in consumer:
        tx = message.value
        insert_transaction(conn, tx)

if __name__ == "__main__":
    main()
