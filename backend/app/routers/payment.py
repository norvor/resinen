# backend/app/routers/payment.py
from fastapi import APIRouter, Header, HTTPException, Body
from pydantic import BaseModel
import razorpay
import sqlite3
from .auth import get_user_from_token, DB_FILE

router = APIRouter(prefix="/payment", tags=["payment"])

# --- CONFIG ---
KEY_ID = "rzp_test_YOUR_KEY_ID"     # <--- REPLACE THIS
KEY_SECRET = "YOUR_KEY_SECRET"      # <--- REPLACE THIS

client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))

@router.post("/create-order")
def create_order(x_token: str = Header(None)):
    user = get_user_from_token(x_token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Amount is in PAISE (100 paise = 1 Rupee). 
        # ₹499 = 49900 paise.
        data = { "amount": 49900, "currency": "INR", "receipt": x_token }
        order = client.order.create(data=data)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class VerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/verify")
def verify_payment(data: VerifyRequest, x_token: str = Header(None)):
    user = get_user_from_token(x_token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Verify Signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': data.razorpay_order_id,
            'razorpay_payment_id': data.razorpay_payment_id,
            'razorpay_signature': data.razorpay_signature
        })
        
        # If no exception, signature is valid. Upgrade User.
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET is_premium=1, payment_id=? WHERE token=?", 
                  (data.razorpay_payment_id, x_token))
        conn.commit()
        conn.close()
        
        return {"status": "success", "is_premium": True}
        
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))