from database.transactions import TransactionDB
import logging

logger = logging.getLogger(__name__)

def update_transaction(user_id: str, client_id: str, transaction_id: int,
                      amount: float = None, type: str = None, 
                      sub_type: str = None, whom_to_paid: str = None) -> dict:
    """
    Update an existing transaction
    Called by Gemini when user wants to modify a transaction
    """
    try:
        # Validate transaction_id
        if not transaction_id or transaction_id <= 0:
            return {
                "success": False,
                "message": "Invalid transaction ID"
            }
        
        # Build updates dictionary
        updates = {}
        
        if amount is not None:
            if amount <= 0:
                return {
                    "success": False,
                    "message": "Amount must be greater than 0"
                }
            updates["amount"] = amount
        
        if type is not None:
            updates["type"] = type
        
        if sub_type is not None:
            updates["sub_type"] = sub_type
        
        if whom_to_paid is not None:
            updates["whom_to_paid"] = whom_to_paid
        
        # Check if we have any updates
        if not updates:
            return {
                "success": False,
                "message": "No fields to update"
            }
        
        # Get the original transaction for comparison
        original_result = TransactionDB.get_transaction_by_id(
            transaction_id=transaction_id,
            user_id=user_id,
            client_id=client_id
        )
        
        if not original_result["success"]:
            return {
                "success": False,
                "message": "Transaction not found"
            }
        
        original_tx = original_result["transaction"]
        
        # Update the transaction
        result = TransactionDB.update_transaction(
            transaction_id=transaction_id,
            user_id=user_id,
            client_id=client_id,
            updates=updates
        )
        
        if result["success"]:
            # Build response message
            changes = []
            
            if "amount" in updates:
                old_amount = original_tx["amount"]
                new_amount = updates["amount"]
                changes.append(f"amount: ₹{old_amount} → ₹{new_amount}")
            
            if "type" in updates:
                old_type = original_tx["type"]
                new_type = updates["type"]
                changes.append(f"type: {old_type} → {new_type}")
            
            if "sub_type" in updates:
                old_sub_type = original_tx.get("sub_type", "N/A")
                new_sub_type = updates["sub_type"]
                changes.append(f"category: {old_sub_type} → {new_sub_type}")
            
            if "whom_to_paid" in updates:
                old_whom = original_tx.get("whom_to_paid", "N/A")
                new_whom = updates["whom_to_paid"]
                changes.append(f"person: {old_whom} → {new_whom}")
            
            changes_text = ", ".join(changes)
            message = f"Updated transaction #{transaction_id}: {changes_text}"
            
            return {
                "success": True,
                "message": message,
                "data": {
                    "transaction_id": transaction_id,
                    "changes": updates
                }
            }
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error in update_transaction tool: {e}")
        return {
            "success": False,
            "message": f"Error updating transaction: {str(e)}"
        } 