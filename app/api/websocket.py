from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.websocket_manager import manager
from app.core.security import get_user_id_from_token
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Messages, User
from datetime import datetime, timezone
from app.services.ai_service import ask_ai
from app.db.models import Messages, User, Cards, Columns

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
                content = data["content"]

                sender = db.query(User).filter(User.user_id == user_id).first()

                if content.lower().startswith("@ai"):
                    # AI bot response
                    ai_question = content[3:].strip()  # убираем "@ai" из начала
                    # TODO: вызвать AI и сохранить ответ

                    # Get board cards as context for AI
                    columns = (
                        db.query(Columns).filter(Columns.board_id == board_id).all()
                    )
                    cards_context = []
                    for col in columns:
                        cards = (
                            db.query(Cards)
                            .filter(Cards.column_id == col.column_id)
                            .all()
                        )
                        for card in cards:
                            cards_context.append(f"[{col.name}] {card.name}")

                    context_text = (
                        "\n".join(cards_context) if cards_context else "No cards yet"
                    )

                    system_prompt = f"""You are a helpful AI assistant for a Kanban board.
                    Current board cards:
                    {context_text}

                    Answer questions about the board tasks briefly and helpfully."""

                    ai_response = await ask_ai(system_prompt, ai_question)

                    ai_message = Messages(
                        board_id=board_id,
                        user_id=user_id,
                        content=ai_response,
                        created_at=datetime.now(timezone.utc),
                        is_ai=True,
                    )
                    db.add(ai_message)
                    db.commit()
                    db.refresh(ai_message)

                    await manager.publish(
                        board_id,
                        {
                            "action": "message_added",
                            "message": {
                                "id": ai_message.id,
                                "user_id": ai_message.user_id,
                                "nickname": "AI Assistant",
                                "content": ai_message.content,
                                "is_ai": ai_message.is_ai,
                                "created_at": ai_message.created_at.isoformat(),
                            },
                        },
                    )

                else:

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
