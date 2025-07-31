# FarmerX – Smart Finance Management API

A smart finance management backend powered by FastAPI + Gemini Function Calling, where users manage their income and expenses using natural language.

## 🎯 Overview

FarmerX is designed to replace traditional form-based inputs with intelligent natural language processing. Users interact via plain text (converted from speech by frontend) and Gemini intelligently:

- Parses the message
- Extracts intent + entities  
- Calls the appropriate internal tools (add, get, update, delete)

Everything works dynamically through Gemini — no manual parsing or hardcoding involved.

## 🏗️ Architecture

```
farmer_x/
│
├── llm/                     # Gemini LLM & function calling setup
│   ├── gemini_llm.py        # Gemini config + function schema registration
│   ├── router.py            # Endpoint to receive messages and invoke Gemini
│   └── tools/               # Tools that Gemini calls directly
│       ├── add_transaction.py
│       ├── get_transaction.py
│       ├── update_transaction.py
│       └── delete_transaction.py
│
├── database/                # DB layer with raw SQL or query helpers
│   ├── connection.py        # MySQL connection setup
│   └── transactions.py      # All DB operations
│
├── schema/                  # Pydantic request/response models
│   └── transaction_schema.py
│
├── config/                  # App settings, secrets, envs
│   ├── settings.py
│   └── env.py
│
├── utils/                   # Generic helper functions
│   └── date_utils.py        # Date filtering utilities
│
├── main.py                  # FastAPI entry point
└── requirements.txt         # Project dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=farmer_x

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 3. Setup Database

Create a MySQL database named `farmer_x` (or as specified in your .env file).

### 4. Run the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Main Endpoint

**POST** `/llm/transaction-message`

Process natural language messages and execute appropriate actions.

**Request Body:**
```json
{
  "user_id": "abc123",
  "client_id": "farmer_x",
  "message": "I paid 500 to the vet for animal checkup"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Added expense of ₹500 (veterinary) to vet",
  "data": {
    "amount": 500,
    "type": "expense",
    "sub_type": "veterinary",
    "whom_to_paid": "vet"
  },
  "tool_called": "add_transaction"
}
```

### Health Check

**GET** `/health`

Check API and database status.

### Direct Transaction Access

**GET** `/transactions/{user_id}/{client_id}`

Get transactions with optional filters (for debugging/testing).

## 🧠 Smart Agent Behavior

The system can understand and process various natural language inputs:

### Adding Transactions
- "I sold 10kg tomatoes for 1200 today"
- "Paid 800 for fertilizers yesterday"
- "Received 5000 salary from company"

### Viewing Transactions
- "Show me all expenses from this month"
- "What are my incomes today?"
- "Display transactions above 1000 rupees"

### Updating Transactions
- "Update the 500 rs grocery to 600"
- "Change yesterday's fertilizer expense to 900"

### Deleting Transactions
- "Delete the last transaction"
- "Remove the 500 expense from yesterday"

## 🗃️ Database Schema

```sql
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    amount FLOAT NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    sub_type VARCHAR(100),
    whom_to_paid VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_client (user_id, client_id),
    INDEX idx_created_at (created_at)
);
```

## 🧪 Testing Examples

### Test Adding Income
```bash
curl -X POST "http://localhost:8000/llm/transaction-message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "farmer123",
    "client_id": "farmer_x",
    "message": "I sold 20kg wheat for 4000 today"
  }'
```

### Test Adding Expense
```bash
curl -X POST "http://localhost:8000/llm/transaction-message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "farmer123",
    "client_id": "farmer_x",
    "message": "Paid 1500 for seeds and fertilizers"
  }'
```

### Test Viewing Transactions
```bash
curl -X POST "http://localhost:8000/llm/transaction-message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "farmer123",
    "client_id": "farmer_x",
    "message": "Show me all expenses from this month"
  }'
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MySQL host | localhost |
| `DB_PORT` | MySQL port | 3306 |
| `DB_USER` | MySQL username | root |
| `DB_PASSWORD` | MySQL password | "" |
| `DB_NAME` | Database name | farmer_x |
| `GEMINI_API_KEY` | Gemini API key | "" |
| `API_HOST` | API host | 0.0.0.0 |
| `API_PORT` | API port | 8000 |
| `DEBUG` | Debug mode | False |

## 🛠️ Development

### Project Structure

- **LLM Layer**: Handles natural language processing with Gemini
- **Router**: Routes messages to appropriate tools
- **Tools**: Individual functions for CRUD operations
- **Database**: MySQL operations with connection management
- **Schema**: Pydantic models for request/response validation

### Adding New Tools

1. Create a new tool function in `llm/tools/`
2. Add it to the tools dictionary in `llm/router.py`
3. Update the function schema in `llm/gemini_llm.py`

### Error Handling

The system includes comprehensive error handling:
- Database connection errors
- Invalid input validation
- Gemini API errors
- Tool execution errors

## 📊 Features

- ✅ Natural language processing with Gemini
- ✅ CRUD operations for transactions
- ✅ Smart date filtering (today, yesterday, this week, etc.)
- ✅ Amount-based filtering
- ✅ Category-based organization
- ✅ Comprehensive error handling
- ✅ RESTful API design
- ✅ Database connection management
- ✅ Logging and monitoring

## 🔒 Security Considerations

- Database credentials loaded from environment variables
- Input validation with Pydantic models
- SQL injection prevention with parameterized queries
- CORS configuration for frontend integration

## 🚀 Deployment

### Production Setup

1. Set `DEBUG=False` in environment
2. Configure proper CORS origins
3. Use production database credentials
4. Set up proper logging
5. Configure reverse proxy (nginx)

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions, please open an issue in the repository. 