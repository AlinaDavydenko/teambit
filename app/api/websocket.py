from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.websocket_manager import manager
from app.core.security import get_user_id_from_token
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Messages, User
from datetime import datetime, timezone

router = APIRouter()


@router.websocket("/ws/boards/{board_id}")
async def websocket_endpoint(
    websocket: WebSocket, board_id: int, token: str, db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(token)

    if not user_id:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, board_id, user_id)

    # Notify everyone that online list changed
    await manager.publish(
        board_id,
        {
            "action": "online_users_updated",
            "user_ids": manager.get_online_users(board_id),
        },
    )

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "send_message":

                sender = db.query(User).filter(User.user_id == user_id).first()

                new_message = Messages(
                    board_id=board_id,
                    user_id=user_id,
                    content=data["content"],
                    created_at=datetime.now(timezone.utc),
                    is_ai=False,
                )

                db.add(new_message)

                db.commit()

                db.refresh(new_message)

                await manager.publish(
                    board_id,
                    {
                        "action": "message_added",
                        "message": {
                            "id": new_message.id,
                            "user_id": new_message.user_id,
                            "nickname": sender.nickname,
                            "content": new_message.content,
                            "is_ai": new_message.is_ai,
                            "created_at": new_message.created_at.isoformat(),
                        },
                    },
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, board_id)

        await manager.publish(
            board_id,
            {
                "action": "online_users_updated",
                "user_ids": manager.get_online_users(board_id),
            },
        )
