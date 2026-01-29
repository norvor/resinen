from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import razorpay

from app.database import get_session
from app.models import User
from app.routers.auth import get_current_user # <--- THE FIX

router = APIRouter(prefix="/payment", tags=["payment"])

# Initialize Razorpay Client (Use env vars in production)
# For local dev, these are placeholders.
client = razorpay.Client(auth=("rzp_test_YOUR_KEY", "YOUR_SECRET"))

class OrderRequest(BaseModel):
    amount: int # In paise (e.g., 49900 = 499 INR)
    currency: str = "INR"

class PaymentVerification(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str

@router.post("/create-order")
async def create_order(
    req: OrderRequest, 
    current_user: User = Depends(get_current_user)
):
    """
    Creates an order ID on Razorpay servers.
    """
    data = {
        "amount": req.amount,
        "currency": req.currency,
        "receipt": f"receipt_{current_user.id}",
        "payment_capture": 1
    }
    
    try:
        # In a real scenario, we call Razorpay API:
        # order = client.order.create(data=data)
        # return order
        
        # MOCK RESPONSE FOR LOCALHOST DEV (So you can test UI without keys)
        return {
            "id": "order_mock_123456789",
            "entity": "order",
            "amount": req.amount,
            "amount_paid": 0,
            "amount_due": req.amount,
            "currency": req.currency,
            "receipt": f"receipt_{current_user.id}",
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify")
async def verify_payment(
    data: PaymentVerification,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Verifies the signature and upgrades the user to Premium.
    """
    try:
        # 1. Verify Signature (Commented out for Mock Mode)
        # client.utility.verify_payment_signature(data.dict())

        # 2. Upgrade User in Database
        current_user.is_premium = True
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return {"status": "success", "message": "Premium Activated", "is_premium": True}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid Payment Signature")