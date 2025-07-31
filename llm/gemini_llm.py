import google.generativeai as genai
from config.settings import settings
import logging
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class GeminiLLM:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key not found in configuration")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Define available tools/functions
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define the tools that Gemini can call"""
        return [
            {
                "name": "add_transaction",
                "description": "Add a new income or expense transaction",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "The transaction amount"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["income", "expense"],
                            "description": "Whether this is income or expense"
                        },
                        "sub_type": {
                            "type": "string",
                            "description": "Category of the transaction (e.g., grocery, salary, fertilizer)"
                        },
                        "whom_to_paid": {
                            "type": "string",
                            "description": "Person or entity involved in the transaction"
                        }
                    },
                    "required": ["amount", "type"]
                }
            },
            {
                "name": "get_transaction",
                "description": "Get transactions with optional filters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["income", "expense"],
                            "description": "Filter by transaction type"
                        },
                        "sub_type": {
                            "type": "string",
                            "description": "Filter by sub-type/category"
                        },
                        "date_filter": {
                            "type": "string",
                            "description": "Date filter like 'today', 'yesterday', 'this week', 'this month'"
                        },
                        "amount_min": {
                            "type": "number",
                            "description": "Minimum amount filter"
                        },
                        "amount_max": {
                            "type": "number",
                            "description": "Maximum amount filter"
                        }
                    }
                }
            },
            {
                "name": "update_transaction",
                "description": "Update an existing transaction",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "integer",
                            "description": "ID of the transaction to update"
                        },
                        "amount": {
                            "type": "number",
                            "description": "New amount"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["income", "expense"],
                            "description": "New transaction type"
                        },
                        "sub_type": {
                            "type": "string",
                            "description": "New sub-type/category"
                        },
                        "whom_to_paid": {
                            "type": "string",
                            "description": "New person or entity"
                        }
                    },
                    "required": ["transaction_id"]
                }
            },
            {
                "name": "delete_transaction",
                "description": "Delete a transaction by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "integer",
                            "description": "ID of the transaction to delete"
                        }
                    },
                    "required": ["transaction_id"]
                }
            }
        ]
    
    def process_message(self, user_id: str, client_id: str, message: str, 
                       recent_transactions: List[Dict] = None) -> Dict[str, Any]:
        """
        Process natural language message and determine which tool to call
        """
        try:
            # Build context with recent transactions
            context = self._build_context(user_id, client_id, recent_transactions)
            
            # Create the prompt for Gemini
            prompt = self._create_prompt(message, context)
            
            # Call Gemini with function calling
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            # Parse the response to determine which tool to call
            tool_call = self._parse_response(response.text)
            
            return {
                "success": True,
                "tool_call": tool_call,
                "raw_response": response.text
            }
            
        except Exception as e:
            logger.error(f"Error processing message with Gemini: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Unable to process your request. Please try again."
            }
    
    def _build_context(self, user_id: str, client_id: str, 
                      recent_transactions: List[Dict] = None) -> str:
        """Build context string with recent transactions"""
        context = f"User ID: {user_id}, Client ID: {client_id}\n\n"
        
        if recent_transactions:
            context += "Recent transactions for context:\n"
            for tx in recent_transactions[:3]:  # Show last 3 transactions
                context += f"- {tx['type']}: ₹{tx['amount']} ({tx.get('sub_type', 'N/A')}) - {tx['created_at']}\n"
            context += "\n"
        
        return context
    
    def _create_prompt(self, message: str, context: str) -> str:
        """Create the prompt for Gemini"""
        return f"""
You are a smart finance management assistant for farmers. Your job is to understand natural language messages and call the appropriate function.

Primary Transaction Types (as per financial standards):
- income: Money coming in (salary, crop sales, government subsidy, etc.)
- expense: Daily/monthly spendings (seeds, fertilizers, labor, electricity)
- asset: Owned value things (tractor, land, machinery, etc.)
- liability: What they owe — loans, debts, etc.
- loan_given: Money given to someone (friend, family, etc.) — expecting return
- loan_taken: Loan taken from any source (bank, person, etc.)
- investment: Money invested in anything (livestock, mutual fund, land development)
- savings: Amount kept aside intentionally (bank, FD, post office, etc.)
- subsidy: Government-provided money (should be treated as income but tag separately)
- others: For anything that doesn’t fit in above (description will help here)

When extracting the 'type' field, always use the most appropriate value from the above list based on the user's message.

Available functions:
{json.dumps(self.tools, indent=2)}

Context:
{context}

User message: "{message}"

Instructions:
1. Analyze the user's message to understand their intent
2. Determine which function to call based on the message
3. Extract relevant parameters from the message
4. For the 'type' field, use the most appropriate value from the Primary Transaction Types above
5. Return a JSON response with the function name and parameters

For example:
- "I sold 10kg tomatoes for 1200 today" → add_transaction with amount=1200, type="income", sub_type="crop_sale"
- "Show me all expenses from this month" → get_transaction with date_filter="this month", type="expense"
- "Update the 500 rs grocery to 600" → update_transaction with transaction_id (you need to identify which transaction)

Return only a valid JSON object with the function name and parameters. If you cannot determine the intent clearly, return {{"error": "Unable to understand the request"}}.

Response:"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's response to extract function call"""
        try:
            # Try to extract JSON from the response
            response_text = response_text.strip()
            
            # Find JSON object in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                if "error" in parsed:
                    return {"error": parsed["error"]}
                
                # Validate that we have a function name
                if "name" not in parsed:
                    return {"error": "No function name specified"}
                
                return parsed
            else:
                return {"error": "Invalid response format"}
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return {"error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {"error": "Error parsing response"}

# Global Gemini instance
gemini_llm = GeminiLLM() 