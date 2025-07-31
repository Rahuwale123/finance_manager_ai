from database.transactions import TransactionDB
import logging

logger = logging.getLogger(__name__)

def delete_transaction(user_id: str, client_id: str, transaction_id: int) -> dict:
    """
    Delete a transaction by ID
    Called by Gemini when user wants to remove a transaction
    """
    try:
        # Validate transaction_id
        if not transaction_id or transaction_id <= 0:
            return {
                "success": False,
                "message": "Invalid transaction ID"
            }
        
        # Get the transaction details before deletion for confirmation
        transaction_result = TransactionDB.get_transaction_by_id(
            transaction_id=transaction_id,
            user_id=user_id,
            client_id=client_id
        )
        
        if not transaction_result["success"]:
            return {
                "success": False,
                "message": "Transaction not found"
            }
        
        transaction = transaction_result["transaction"]
        
        # Delete the transaction
        result = TransactionDB.delete_transaction(
            transaction_id=transaction_id,
            user_id=user_id,
            client_id=client_id
        )
        
        if result["success"]:
            # Build confirmation message
            amount = transaction["amount"]
            transaction_type = transaction["type"]
            sub_type = transaction.get("sub_type", "")
            whom_to_paid = transaction.get("whom_to_paid", "")
            
            sub_type_text = f" ({sub_type})" if sub_type else ""
            whom_text = f" to {whom_to_paid}" if whom_to_paid else ""
            
            message = f"Deleted {transaction_type} of ₹{amount}{sub_type_text}{whom_text} (ID: {transaction_id})"
            
            return {
                "success": True,
                "message": message,
                "data": {
                    "deleted_transaction": {
                        "id": transaction_id,
                        "amount": amount,
                        "type": transaction_type,
                        "sub_type": sub_type,
                        "whom_to_paid": whom_to_paid
                    }
                }
            }
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error in delete_transaction tool: {e}")
        return {
            "success": False,
            "message": f"Error deleting transaction: {str(e)}"
        } 