from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Board, BoardMembers, User, Columns, Cards
from app.db.schemas import ColumnCreate, ColumnResponse, ColumnUpdate
from app.core.security import get_current_user
from app.services.websocket_manager import manager

router = APIRouter(prefix="/boards")


@router.post("/{board_id}/columns", response_model=ColumnResponse)
async def create_column(
    board_id: int,
    column_data: ColumnCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a column"""
    # Check the existence of the board → 404
    is_board = db.query(Board).filter(Board.board_id == board_id).first()
    if not is_board:
        raise HTTPException(status_code=404, detail="Board is not founded")

    # Check the current user is a member of the board → 403
    user_id = current_user.user_id
    user_is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not user_is_member:
        raise HTTPException(status_code=403, detail="User is not a member of the board")

    columns_count = db.query(Columns).filter(Columns.board_id == board_id).count()
    position = columns_count + 1

    # Create the column with the board_id and the data from ColumnCreate
    new_column = Columns(name=column_data.name, board_id=board_id, position=position)

    db.add(new_column)

    db.commit()

    db.refresh(new_column)

    await manager.broadcast(
        board_id,
        {
            "action": "column_created",
            "column": ColumnResponse.model_validate(new_column).model_dump(),
        },
    )

    return ColumnResponse.model_validate(new_column)


@router.get("/{board_id}/columns", response_model=list[ColumnResponse])
def get_all_board_columns(
    board_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all columns of the one board"""
    # Check the existence of the board → 404
    is_board = db.query(Board).filter(Board.board_id == board_id).first()
    if not is_board:
        raise HTTPException(status_code=404, detail="Board is not founded")

    # Check the current user is a member of the board → 403
    user_id = current_user.user_id
    user_is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not user_is_member:
        raise HTTPException(status_code=403, detail="User is not a member of the board")

    # Return all board's columns sorted by position
    all_sorted_columns = (
        db.query(Columns)
        .filter(Columns.board_id == board_id)
        .order_by(Columns.position)
        .all()
    )

    return all_sorted_columns


@router.patch("/{board_id}/columns/{column_id}", response_model=ColumnResponse)
async def rename_column(
    column_id: int,
    column_data: ColumnUpdate,
    board_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Rename column"""
    # Check the existence of the board → 404
    is_board = db.query(Board).filter(Board.board_id == board_id).first()
    if not is_board:
        raise HTTPException(status_code=404, detail="Board is not founded")

    # Check the current user is a member of the board → 403
    user_id = current_user.user_id
    user_is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not user_is_member:
        raise HTTPException(status_code=403, detail="User is not a member of the board")

    # Search the column using it id → 404
    column = db.query(Columns).filter(Columns.column_id == column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column is not found")

    # Rename it
    column.name = column_data.name

    db.commit()

    db.refresh(column)

    await manager.broadcast(
        board_id,
        {
            "action": "column_renamed",
            "column": ColumnResponse.model_validate(column).model_dump(),
        },
    )

    return ColumnResponse.model_validate(column)


@router.delete("/{board_id}/columns/{column_id}")
async def delete_column(
    column_id: int,
    board_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete one column using it id"""
    # Check the existence of the board → 404
    is_board = db.query(Board).filter(Board.board_id == board_id).first()
    if not is_board:
        raise HTTPException(status_code=404, detail="Board is not founded")

    # Check the current user is a member of the board → 403
    user_id = current_user.user_id
    user_is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not user_is_member:
        raise HTTPException(status_code=403, detail="User is not a member of the board")

    # Find column using column_id. Is my_column on current board? → 404
    my_column = (
        db.query(Columns)
        .filter(Columns.column_id == column_id, Columns.board_id == board_id)
        .first()
    )
    if not my_column:
        raise HTTPException(status_code=404, detail="Column is not found on this board")

    # Delete all cards in column first
    db.query(Cards).filter(Cards.column_id == column_id).delete()

    db.delete(my_column)

    db.commit()

    await manager.broadcast(
        board_id,
        {"action": "column_deleted", "column_id": column_id},
    )

    return {"message": "Column is deleted"}
