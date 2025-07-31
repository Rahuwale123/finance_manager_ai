from database.transactions import TransactionDB
from utils.date_utils import parse_date_filters, format_date_for_display
import logging

logger = logging.getLogger(__name__)

def get_transaction(user_id: str, client_id: str, type: str = None, 
                   sub_type: str = None, date_filter: str = None,
                   amount_min: float = None, amount_max: float = None) -> dict:
    """
    Get transactions with optional filters
    Called by Gemini when user wants to view transactions
    """
    try:
        # Build filters
        filters = {}
        
        if type:
            filters["type"] = type
        
        if sub_type:
            filters["sub_type"] = sub_type
        
        if date_filter:
            date_filters = parse_date_filters(date_filter)
            filters.update(date_filters)
        
        if amount_min is not None:
            filters["amount_min"] = amount_min
        
        if amount_max is not None:
            filters["amount_max"] = amount_max
        
        # Get transactions from database
        result = TransactionDB.get_transactions(
            user_id=user_id,
            client_id=client_id,
            filters=filters
        )
        
        if result["success"]:
            transactions = result["transactions"]
            
            if not transactions:
                # No transactions found
                filter_text = _build_filter_text(filters)
                message = f"No transactions found{filter_text}"
                
                return {
                    "success": True,
                    "message": message,
                    "data": {
                        "transactions": [],
                        "count": 0
                    }
                }
            
            # Format transactions for display
            formatted_transactions = []
            total_amount = 0
            
            for tx in transactions:
                formatted_tx = {
                    "id": tx["id"],
                    "amount": tx["amount"],
                    "type": tx["type"],
                    "sub_type": tx.get("sub_type"),
                    "whom_to_paid": tx.get("whom_to_paid"),
                    "created_at": format_date_for_display(tx["created_at"]),
                    "raw_created_at": tx["created_at"]
                }
                formatted_transactions.append(formatted_tx)
                
                if tx["type"] == "income":
                    total_amount += tx["amount"]
                else:
                    total_amount -= tx["amount"]
            
            # Build response message
            filter_text = _build_filter_text(filters)
            count_text = f"{len(transactions)} transaction{'s' if len(transactions) != 1 else ''}"
            total_text = f"Total: ₹{total_amount:,.2f}"
            
            message = f"Found {count_text}{filter_text}. {total_text}"
            
            return {
                "success": True,
                "message": message,
                "data": {
                    "transactions": formatted_transactions,
                    "count": len(transactions),
                    "total_amount": total_amount
                }
            }
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error in get_transaction tool: {e}")
        return {
            "success": False,
            "message": f"Error retrieving transactions: {str(e)}"
        }

def _build_filter_text(filters: dict) -> str:
    """Build human-readable filter text"""
    filter_parts = []
    
    if filters.get("type"):
        filter_parts.append(f"type: {filters['type']}")
    
    if filters.get("sub_type"):
        filter_parts.append(f"category: {filters['sub_type']}")
    
    if filters.get("date_from") and filters.get("date_to"):
        filter_parts.append("date range specified")
    
    if filters.get("amount_min") or filters.get("amount_max"):
        amount_filter = []
        if filters.get("amount_min"):
            amount_filter.append(f"min: ₹{filters['amount_min']}")
        if filters.get("amount_max"):
            amount_filter.append(f"max: ₹{filters['amount_max']}")
        filter_parts.append(f"amount ({', '.join(amount_filter)})")
    
    if filter_parts:
        return f" with filters: {', '.join(filter_parts)}"
    else:
        return "" 