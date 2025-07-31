from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from schema.transaction_schema import TransactionMessageRequest, LLMResponse
from llm.router import llm_router
from database.transactions import TransactionDB
from database.connection import db
from config.settings import settings
import logging
from datetime import datetime, timedelta
from typing import Optional
from utils.date_utils import parse_date_filters
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FarmerX Smart Finance Management API",
    description="AI-powered finance management for farmers using natural language",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables on startup"""
    try:
        # Initialize database connection
        db.connect()
        
        # Create tables
        TransactionDB.create_table()
        
        logger.info("FarmerX API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connection on shutdown"""
    try:
        db.disconnect()
        logger.info("FarmerX API shutdown successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "FarmerX Smart Finance Management API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        db.get_connection()
        
        return {
            "status": "healthy",
            "database": "connected",
            "llm": "ready"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@app.post("/llm/transaction-message", response_model=LLMResponse)
async def process_transaction_message(request: TransactionMessageRequest):
    """
    Main endpoint for processing natural language transaction messages
    
    This is the core endpoint where users send natural language messages
    and the system uses Gemini to understand and execute the appropriate action.
    """
    try:
        logger.info(f"Processing message for user {request.user_id}: {request.message}")
        
        # Process the message through the LLM router
        response = llm_router.process_message(
            user_id=request.user_id,
            client_id=request.client_id,
            message=request.message
        )
        
        logger.info(f"Response: {response.message}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing transaction message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/transactions_by_filter")
async def transactions_by_filter(
    user_id: str = Query(...),
    client_id: str = Query(...),
    filter: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get transactions by filter (for debugging/manual DB checks)
    - If start_date and end_date are provided, use them.
    - Otherwise, require filter (today, yesterday, this_week, this_month, etc.).
    - If neither is provided, return error.
    """
    filters = {}
    if start_date and end_date:
        filters["date_from"] = start_date
        filters["date_to"] = end_date
    elif filter:
        filters.update(parse_date_filters(filter))
        if not filters:
            return {"error": "Invalid filter value. Use today, yesterday, this_week, this_month, etc."}
    else:
        return {"error": "You must provide either a filter or both start_date and end_date."}
    result = TransactionDB.get_transactions(user_id=user_id, client_id=client_id, filters=filters)
    if result["success"]:
        # Only return the required fields
        return [
            {
                "id": tx["id"],
                "type": tx["type"],
                "amount": tx["amount"],
                "sub_type": tx.get("sub_type"),
                "whom_to_paid": tx.get("whom_to_paid"),
                "created_at": tx["created_at"].isoformat() if hasattr(tx["created_at"], 'isoformat') else str(tx["created_at"])
            }
            for tx in result["transactions"]
        ]
    else:
        return []

@app.get("/balance")
async def get_balance(user_id: str = Query(...), client_id: str = Query(...)):
    """
    Get the total income, expenses, and net balance for the current month
    """
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    filters = {"date_from": month_start, "date_to": next_month}
    result = TransactionDB.get_transactions(user_id=user_id, client_id=client_id, filters=filters)
    income = sum(tx["amount"] for tx in result["transactions"] if tx["type"] == "income")
    expense = sum(tx["amount"] for tx in result["transactions"] if tx["type"] == "expense")
    return {
        "status": "success",
        "month": now.strftime("%B %Y"),
        "income": income,
        "expense": expense,
        "net_balance": income - expense
    }

@app.delete("/transaction/{transaction_id}")
async def delete_transaction(
    transaction_id: int = Path(...),
    user_id: str = Query(...),
    client_id: str = Query(...)
):
    """
    Delete a transaction by ID
    """
    result = TransactionDB.delete_transaction(transaction_id, user_id, client_id)
    if result["success"]:
        return {"status": "success", "message": "Transaction deleted successfully."}
    else:
        return {"status": "error", "message": result.get("message", "Delete failed.")}

class UpdateTransactionAmountPayload(BaseModel):
    user_id: str
    client_id: str
    amount: float

@app.put("/transaction/{transaction_id}")
async def update_transaction(
    transaction_id: int = Path(...),
    payload: UpdateTransactionAmountPayload = None
):
    """
    Update only the amount of a transaction by ID
    """
    user_id = payload.user_id
    client_id = payload.client_id
    amount = payload.amount
    updates = {"amount": amount}
    result = TransactionDB.update_transaction(transaction_id, user_id, client_id, updates)
    if result["success"]:
        return {"status": "success", "message": "Transaction updated successfully."}
    else:
        return {"status": "error", "message": result.get("message", "Update failed.")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    ) 