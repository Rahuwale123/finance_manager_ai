from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionMessageRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    client_id: str = Field(..., description="Client ID")
    message: str = Field(..., description="Natural language message")

class TransactionResponse(BaseModel):
    id: int
    client_id: str
    user_id: str
    amount: float
    type: TransactionType
    sub_type: Optional[str] = None
    whom_to_paid: Optional[str] = None
    created_at: datetime

class TransactionListResponse(BaseModel):
    success: bool
    transactions: List[TransactionResponse]
    message: Optional[str] = None

class TransactionSingleResponse(BaseModel):
    success: bool
    transaction: Optional[TransactionResponse] = None
    message: Optional[str] = None

class LLMResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    tool_called: Optional[str] = None

class AddTransactionRequest(BaseModel):
    client_id: str
    user_id: str
    amount: float = Field(..., gt=0, description="Transaction amount")
    type: TransactionType
    sub_type: Optional[str] = None
    whom_to_paid: Optional[str] = None

class GetTransactionRequest(BaseModel):
    user_id: str
    client_id: str
    filters: Optional[Dict[str, Any]] = None

class UpdateTransactionRequest(BaseModel):
    transaction_id: int
    user_id: str
    client_id: str
    updates: Dict[str, Any] = Field(..., description="Fields to update")

class DeleteTransactionRequest(BaseModel):
    transaction_id: int
    user_id: str
    client_id: str 