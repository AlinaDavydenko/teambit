from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Board, BoardMembers
from app.db.schemas import BoardCreate, BoardResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/boards")


@router.post("/", response_model=BoardResponse)
def create_board(
    board_data: BoardCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    # Get user_id
    user_id = current_user.user_id

    new_board = Board(name=board_data.name, color=board_data.color, user_id=user_id)

    db.add(new_board)

    db.commit()

    db.refresh(new_board)

    # find a board id
    board_id = new_board.board_id

    member_object = BoardMembers(board_id=board_id, user_id=user_id, role="owner")

    db.add(member_object)

    db.commit()

    db.refresh(member_object)

    return BoardResponse.model_validate(new_board)


@router.get("/", response_model=list[BoardResponse])
def get_all_boards(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Find all user's boards"""
    # Get user_id
    user_id = current_user.user_id
    boards = (
        db.query(Board).join(BoardMembers).filter(BoardMembers.user_id == user_id).all()
    )

    return boards


@router.get("/{board_id}", response_model=BoardResponse)
def get_one_board(
    board_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get one board using it's id"""
    # Get user_id
    user_id = current_user.user_id

    board = db.query(Board).filter(Board.board_id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Access denied")

    return board


@router.delete("/{board_id}")
def delete_board(
    board_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete board using it id"""
    # Get user_id
    user_id = current_user.user_id

    # Get board using board_id
    board = db.query(Board).filter(Board.board_id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    # Get board_id

    # Is current user owner?
    member = (
        db.query(BoardMembers)
        .filter(BoardMembers.user_id == user_id, BoardMembers.board_id == board_id)
        .first()
    )

    if not member:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get member's role
    member_role = member.role
    if member_role != "owner":
        raise HTTPException(status_code=403, detail="User is not owner")

    db.delete(board)

    db.commit()

    return {"message": "Board deleted successfully"}


# TODO:
# DELETE /boards/{id}               — удалить доску
# POST   /boards/{id}/members       — добавить участника
# DELETE /boards/{id}/members/{uid} — удалить участника
# PATCH  /boards/{id}/transfer      — передать доску другому владельцу
