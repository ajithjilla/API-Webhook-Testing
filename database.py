# database.py
# Database models and fake data storage

from typing import Dict, Any

# In-memory user database
fake_users_db: Dict[str, Dict[str, Any]] = {
    "user1": {
        "id": "user1",
        "mail": "john@example.com",
        "name": "John Doe",
        "phone": "+1-234-567-8900",
        "password": "hashed_password_123",
        "created_at": "2024-01-01T10:00:00Z"
    },
    "user2": {
        "id": "user2",
        "mail": "jane@example.com",
        "name": "Jane Smith",
        "phone": "+1-987-654-3210",
        "password": "hashed_password_456",
        "created_at": "2024-01-02T10:00:00Z"
    }
}
