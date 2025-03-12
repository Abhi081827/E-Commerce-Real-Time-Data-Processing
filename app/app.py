
import os

import logging
from fastapi import FastAPI, HTTPException
import psycopg2
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPI-App")



app = FastAPI()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            dbname=os.getenv("POSTGRES_DB", "financial_db")
        )
        return conn
    except Exception as e:
        logger.error(f"DB Connection Error: {e}")
        raise HTTPException(status_code=500, detail=f"DB Connection Error: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/transactions/all")
def get_all_transactions():
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT transaction_id, timestamp, customer_id, product_category,
               product_id, price, quantity, payment_method,
               shipping_country, shipping_city, discount_percent,
               shipping_method, shipping_cost, order_total
        FROM ecommerce_transactions
        ORDER BY timestamp DESC;
    """
    try:
        cur.execute(query)
        rows = cur.fetchall()
    except Exception as e:
        cur.close()
        conn.close()
        logger.error(f"Query Execution Error: {e}")
        raise HTTPException(status_code=500, detail=f"Query Execution Error: {e}")
    
    cur.close()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "transaction_id": row[0],
            "timestamp": row[1].isoformat() if row[1] else None,
            "customer_id": row[2],
            "product_category": row[3],
            "product_id": row[4],
            "price": float(row[5]),
            "quantity": row[6],
            "payment_method": row[7],
            "shipping_country": row[8],
            "shipping_city": row[9],
            "discount_percent": float(row[10]),
            "shipping_method": row[11],
            "shipping_cost": float(row[12]),
            "order_total": float(row[13])
        })
    return {"all_transactions": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
