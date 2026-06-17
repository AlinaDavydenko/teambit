from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Cards, Columns, BoardMembers
from app.db.schemas import CardCreate, CardResponse, CardUpdate, CardMove
from app.core.security import get_current_user
from app.services.websocket_manager import manager

router = APIRouter(prefix="/cards")


@router.post("/columns/{column_id}/card", response_model=CardResponse)
async def create_card(
    column_id: int,
    card_data: CardCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create card"""
    # User's id
    user_id = current_user.user_id

    # The existence of the column → 404
    column = db.query(Columns).filter(Columns.column_id == column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column is not founded")

    # Find board_id
    board_id = column.board_id

    # Check if a current user is the member of the board → 403
    is_user = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not is_user:
        raise HTTPException(status_code=403, detail="User is not a member of the board")

    # Find a position
    cards_count = db.query(Cards).filter(Cards.column_id == column_id).count()
    position = cards_count + 1

    # Create a card
    new_card = Cards(
        name=card_data.name,
        color=card_data.color,
        task_description=card_data.task_description,
        column_id=column.column_id,
        position=position,
        priority=card_data.priority,
        tags=card_data.tags,
        deadline=card_data.deadline,
        is_template=False,
    )

    db.add(new_card)

    db.commit()

    db.refresh(new_card)

    await manager.broadcast(
        board_id,
        {
            "action": "card_created",
            "card": CardResponse.model_validate(new_card).model_dump(),
        },
    )

    return CardResponse.model_validate(new_card)


@router.get("/columns/{column_id}/cards", response_model=list[CardResponse])
def get_all_cards(
    column_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all cards of the column"""
    # Check the existance of the column → 404
    column = db.query(Columns).filter(Columns.column_id == column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column is not founded")

    # Find board_id using column
    board_id = column.board_id

    # Check if current user is a member of the board → 403
    user_id = current_user.user_id
    is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="User is not a member of the board")

    # Find all cards sorted by position
    all_sorted_cards = (
        db.query(Cards)
        .filter(Cards.column_id == column_id)
        .order_by(Cards.position)
        .all()
    )

    return all_sorted_cards


@router.patch("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: int,
    card_data: CardUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a card"""
    # Find card using card_id → 404
    card = db.query(Cards).filter(Cards.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card is not found")

    # Find the column_id
    column_id = card.column_id

    # Find board_id using column
    column = db.query(Columns).filter(Columns.column_id == column_id).first()
    board_id = column.board_id

    # Check if current user is a member of the board → 403
    user_id = current_user.user_id
    is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="User is not a member of the board")

    # Update fields
    update_data = card_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(card, field, value)

    db.commit()

    db.refresh(card)

    await manager.broadcast(
        board_id,
        {
            "action": "card_update",
            "card": CardResponse.model_validate(card).model_dump(),
        },
    )

    return CardResponse.model_validate(card)


@router.delete("/{card_id}")
async def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a card"""
    # Find card using card_id → 404
    card = db.query(Cards).filter(Cards.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card is not found")

    # Find the column_id
    column_id = card.column_id

    # Find board_id using column
    column = db.query(Columns).filter(Columns.column_id == column_id).first()
    board_id = column.board_id

    # Check if current user is a member of the board → 403
    user_id = current_user.user_id
    is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="User is not a member of the board")

    # Delete the card
    db.delete(card)

    db.commit()

    await manager.broadcast(board_id, {"action": "card_deleted", "card_id": card_id})

    return {"message": "The card is deleted"}


@router.patch("/{card_id}/move", response_model=CardResponse)
async def card_move(
    card_id: int,
    card_data: CardMove,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Change the column of the card"""
    # Find the card → 404
    card = db.query(Cards).filter(Cards.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card is not found")

    # Check if current user is a member of the board → 403
    # Find the column_id
    column_id = card.column_id

    # Find board_id using column
    column = db.query(Columns).filter(Columns.column_id == column_id).first()
    board_id = column.board_id

    user_id = current_user.user_id
    is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="User is not a member of the board")

    # Check if new column exists and stays the same board → 404
    new_column = (
        db.query(Columns)
        .filter(Columns.column_id == card_data.column_id, Columns.board_id == board_id)
        .first()
    )
    if not new_column:
        raise HTTPException(
            status_code=404, detail="Column is not exists on the current board"
        )

    # Update column_id & position
    card.column_id = card_data.column_id
    card.position = card_data.position

    db.commit()

    db.refresh(card)

    await manager.broadcast(
        board_id,
        {
            "action": "card_moved",
            "card": CardResponse.model_validate(card).model_dump(),
        },
    )

    return CardResponse.model_validate(card)
