from llm.gemini_llm import gemini_llm
from database.transactions import TransactionDB
from llm.tools.add_transaction import add_transaction
from llm.tools.get_transaction import get_transaction
from llm.tools.update_transaction import update_transaction
from llm.tools.delete_transaction import delete_transaction
from schema.transaction_schema import LLMResponse
import logging

logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(self):
        self.tools = {
            "add_transaction": add_transaction,
            "get_transaction": get_transaction,
            "update_transaction": update_transaction,
            "delete_transaction": delete_transaction
        }
    
    def process_message(self, user_id: str, client_id: str, message: str) -> LLMResponse:
        """
        Main entry point for processing natural language messages
        """
        try:
            # Get recent transactions for context
            recent_result = TransactionDB.get_recent_transactions(
                user_id=user_id,
                client_id=client_id,
                limit=5
            )
            
            recent_transactions = []
            if recent_result["success"]:
                recent_transactions = recent_result["transactions"]
            
            # Process message with Gemini
            gemini_result = gemini_llm.process_message(
                user_id=user_id,
                client_id=client_id,
                message=message,
                recent_transactions=recent_transactions
            )
            
            if not gemini_result["success"]:
                return LLMResponse(
                    success=False,
                    message=gemini_result.get("message", "Unable to process request"),
                    tool_called=None
                )
            
            tool_call = gemini_result["tool_call"]
            
            # Check for errors in tool call
            if "error" in tool_call:
                return LLMResponse(
                    success=False,
                    message=tool_call["error"],
                    tool_called=None
                )
            
            # Execute the appropriate tool
            tool_name = tool_call.get("name")
            tool_params = tool_call.get("parameters", {})
            
            if tool_name not in self.tools:
                return LLMResponse(
                    success=False,
                    message=f"Unknown tool: {tool_name}",
                    tool_called=tool_name
                )
            
            # Add user_id and client_id to tool parameters
            tool_params["user_id"] = user_id
            tool_params["client_id"] = client_id
            
            # Call the tool
            tool_result = self.tools[tool_name](**tool_params)
            
            return LLMResponse(
                success=tool_result["success"],
                message=tool_result["message"],
                data=tool_result.get("data"),
                tool_called=tool_name
            )
            
        except Exception as e:
            logger.error(f"Error in LLM router: {e}")
            return LLMResponse(
                success=False,
                message=f"Internal error: {str(e)}",
                tool_called=None
            )

# Global router instance
llm_router = LLMRouter() 