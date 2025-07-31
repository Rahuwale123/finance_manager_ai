from database.connection import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TransactionDB:
    
    @staticmethod
    def create_table():
        """Create transactions table if not exists"""
        query = """
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            client_id VARCHAR(50) NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            amount FLOAT NOT NULL,
            type VARCHAR(32) NOT NULL,
            sub_type VARCHAR(100),
            whom_to_paid VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_client (user_id, client_id),
            INDEX idx_created_at (created_at)
        )
        """
        try:
            db.execute_update(query)
            logger.info("Transactions table created/verified")
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise e
    
    @staticmethod
    def add_transaction(client_id: str, user_id: str, amount: float, 
                       transaction_type: str, sub_type: str = None, 
                       whom_to_paid: str = None):
        """Add a new transaction"""
        query = """
        INSERT INTO transactions (client_id, user_id, amount, type, sub_type, whom_to_paid)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (client_id, user_id, amount, transaction_type, sub_type, whom_to_paid)
        
        try:
            affected_rows = db.execute_update(query, params)
            if affected_rows > 0:
                logger.info(f"Transaction added successfully: {amount} {transaction_type}")
                return {"success": True, "message": "Transaction added successfully"}
            else:
                return {"success": False, "message": "Failed to add transaction"}
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            raise e
    
    @staticmethod
    def get_transactions(user_id: str, client_id: str, filters: dict = None):
        """Get transactions with optional filters"""
        query = """
        SELECT * FROM transactions 
        WHERE user_id = %s AND client_id = %s
        """
        params = [user_id, client_id]
        
        # Add filters
        if filters:
            if filters.get('type'):
                query += " AND type = %s"
                params.append(filters['type'])
            
            if filters.get('sub_type'):
                query += " AND sub_type = %s"
                params.append(filters['sub_type'])
            
            if filters.get('date_from'):
                query += " AND created_at >= %s"
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                query += " AND created_at <= %s"
                params.append(filters['date_to'])
            
            if filters.get('amount_min'):
                query += " AND amount >= %s"
                params.append(filters['amount_min'])
            
            if filters.get('amount_max'):
                query += " AND amount <= %s"
                params.append(filters['amount_max'])
        
        query += " ORDER BY created_at DESC"
        
        try:
            results = db.execute_query(query, tuple(params))
            return {"success": True, "transactions": results}
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            raise e
    
    @staticmethod
    def get_transaction_by_id(transaction_id: int, user_id: str, client_id: str):
        """Get a specific transaction by ID"""
        query = """
        SELECT * FROM transactions 
        WHERE id = %s AND user_id = %s AND client_id = %s
        """
        params = (transaction_id, user_id, client_id)
        
        try:
            results = db.execute_query(query, params)
            if results:
                return {"success": True, "transaction": results[0]}
            else:
                return {"success": False, "message": "Transaction not found"}
        except Exception as e:
            logger.error(f"Error getting transaction by ID: {e}")
            raise e
    
    @staticmethod
    def update_transaction(transaction_id: int, user_id: str, client_id: str, 
                          updates: dict):
        """Update a transaction"""
        # Build dynamic update query
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            if field in ['amount', 'type', 'sub_type', 'whom_to_paid']:
                set_clauses.append(f"{field} = %s")
                params.append(value)
        
        if not set_clauses:
            return {"success": False, "message": "No valid fields to update"}
        
        query = f"""
        UPDATE transactions 
        SET {', '.join(set_clauses)}
        WHERE id = %s AND user_id = %s AND client_id = %s
        """
        params.extend([transaction_id, user_id, client_id])
        
        try:
            affected_rows = db.execute_update(query, tuple(params))
            if affected_rows > 0:
                return {"success": True, "message": "Transaction updated successfully"}
            else:
                return {"success": False, "message": "Transaction not found or no changes made"}
        except Exception as e:
            logger.error(f"Error updating transaction: {e}")
            raise e
    
    @staticmethod
    def delete_transaction(transaction_id: int, user_id: str, client_id: str):
        """Delete a transaction"""
        query = """
        DELETE FROM transactions 
        WHERE id = %s AND user_id = %s AND client_id = %s
        """
        params = (transaction_id, user_id, client_id)
        
        try:
            affected_rows = db.execute_update(query, params)
            if affected_rows > 0:
                return {"success": True, "message": "Transaction deleted successfully"}
            else:
                return {"success": False, "message": "Transaction not found"}
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            raise e
    
    @staticmethod
    def get_recent_transactions(user_id: str, client_id: str, limit: int = 5):
        """Get recent transactions for context"""
        query = """
        SELECT * FROM transactions 
        WHERE user_id = %s AND client_id = %s
        ORDER BY created_at DESC 
        LIMIT %s
        """
        params = (user_id, client_id, limit)
        
        try:
            results = db.execute_query(query, params)
            return {"success": True, "transactions": results}
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            raise e 