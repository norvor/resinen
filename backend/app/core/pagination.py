import base64
import json
from typing import Generic, TypeVar, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Session, select, SQLModel
from sqlalchemy import desc, tuple_

T = TypeVar("T")

class CursorPage(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[str] = None
    has_next: bool = False

def encode_cursor(timestamp: datetime, id: Any) -> str:
    """
    Encodes the tie-breaker cursor into a URL-safe Base64 string.
    Format: JSON [iso_timestamp, str_id] -> Base64
    """
    payload = [timestamp.isoformat(), str(id)]
    json_str = json.dumps(payload)
    return base64.urlsafe_b64encode(json_str.encode()).decode()

def decode_cursor(cursor: str) -> Optional[tuple[datetime, str]]:
    """Decodes the cursor string back into python objects."""
    try:
        json_str = base64.urlsafe_b64decode(cursor.encode()).decode()
        data = json.loads(json_str)
        return (datetime.fromisoformat(data[0]), data[1])
    except Exception:
        return None

def paginate(
    session: Session,
    query: Any,
    limit: int = 20,
    cursor: Optional[str] = None,
    model: Any = None  # The SQLModel class (e.g., Post)
) -> CursorPage[T]:
    """
    Executes a high-performance Keyset Pagination query.
    Assumes ordering by `created_at DESC, id DESC`.
    """
    
    # 1. Apply Cursor Filter (Seek Logic)
    if cursor and model:
        decoded = decode_cursor(cursor)
        if decoded:
            timestamp, uid = decoded
            # SQL: WHERE (created_at, id) < (timestamp, uid)
            # This uses the composite index efficiently
            query = query.where(
                tuple_(model.created_at, model.id) < (timestamp, uid)
            )

    # 2. Apply Sorting (Always deterministic)
    if model:
        query = query.order_by(desc(model.created_at), desc(model.id))

    # 3. Fetch (Limit + 1 to check for next page)
    query = query.limit(limit + 1)
    results = session.exec(query).all()

    # 4. Process Results
    items = list(results)
    has_next = False
    next_cursor = None

    if len(items) > limit:
        has_next = True
        items = items[:-1]  # Remove the extra item
        
        # Generate cursor from the last item
        last_item = items[-1]
        next_cursor = encode_cursor(last_item.created_at, last_item.id)

    return CursorPage(
        items=items,
        next_cursor=next_cursor,
        has_next=has_next
    )