from database.transactions import TransactionDB
from utils.date_utils import parse_date_filters
import logging

logger = logging.getLogger(__name__)

def add_transaction(user_id: str, client_id: str, amount: float, 
                   type: str, sub_type: str = None, 
                   whom_to_paid: str = None) -> dict:
    """
    Add a new transaction to the database
    Called by Gemini when user wants to add income/expense/other types
    """
    try:
        # Validate input
        if amount <= 0:
            return {
                "success": False,
                "message": "Amount must be greater than 0"
            }
        # Accept any type (income, expense, asset, liability, etc.)
        # Add transaction to database
        result = TransactionDB.add_transaction(
            client_id=client_id,
            user_id=user_id,
            amount=amount,
            transaction_type=type,
            sub_type=sub_type,
            whom_to_paid=whom_to_paid
        )
        
        if result["success"]:
            # Format response message
            type_text = type
            sub_type_text = f" ({sub_type})" if sub_type else ""
            whom_text = f" to {whom_to_paid}" if whom_to_paid else ""
            
            message = f"Added {type_text} of ₹{amount}{sub_type_text}{whom_text}"
            
            return {
                "success": True,
                "message": message,
                "data": {
                    "amount": amount,
                    "type": type,
                    "sub_type": sub_type,
                    "whom_to_paid": whom_to_paid
                }
            }
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error in add_transaction tool: {e}")
        return {
            "success": False,
            "message": f"Error adding transaction: {str(e)}"
        } 