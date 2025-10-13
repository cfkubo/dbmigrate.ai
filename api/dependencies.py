from fastapi import Header, HTTPException

async def get_current_user(x_user_id: str = Header(...)):
    # In a real application, you would validate the user ID against your authentication system.
    # For now, we'll just return the provided user ID.
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header missing")
    return x_user_id
