from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Board, BoardMembers, User, Columns, Cards
from app.db.schemas import (
    BoardCreate,
    BoardResponse,
    AddMember,
    BoardColorUpdate,
    BoardMemberResponse,
)
from app.core.security import get_current_user
from app.services.websocket_manager import manager

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
async def delete_board(
    board_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete board using it id"""
    # Get user_id
    user_id = current_user.user_id

    # Is board?
    board = db.query(Board).filter(Board.board_id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

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

    # Delete all cards
    columns = db.query(Columns).filter(Columns.board_id == board_id).all()
    for column in columns:
        db.query(Cards).filter(Cards.column_id == column.column_id).delete()

    # Delete all columns
    db.query(Columns).filter(Columns.board_id == board_id).delete()

    # Delete all members
    db.query(BoardMembers).filter(BoardMembers.board_id == board_id).delete()

    # Delete the board

    db.delete(board)

    db.commit()

    await manager.publish(board_id, {"action": "board_deleted", "board_id": board_id})

    return {"message": "Board deleted successfully"}


@router.post("/{board_id}/members")
async def add_member(
    board_id: int,
    member_data: AddMember,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Add member to the board"""
    user_id = current_user.user_id
    add_user_id = member_data.user_id

    # Is board?
    board = db.query(Board).filter(Board.board_id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Get member's role
    member = (
        db.query(BoardMembers)
        .filter(BoardMembers.user_id == user_id, BoardMembers.board_id == board_id)
        .first()
    )

    if not member:
        raise HTTPException(status_code=403, detail="Access denied")

    member_role = member.role
    if member_role != "owner":
        raise HTTPException(status_code=403, detail="User is not owner")

    # Check user that we want to add
    new_user = db.query(User).filter(User.user_id == add_user_id).first()
    if not new_user:
        raise HTTPException(status_code=404, detail="User is not founded")

    # If new_user is member?
    is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == add_user_id)
        .first()
    )

    if is_member:
        raise HTTPException(status_code=400, detail="User is member yet")

    user_object = BoardMembers(board_id=board_id, user_id=add_user_id, role="member")

    db.add(user_object)

    db.commit()

    db.refresh(user_object)

    await manager.publish(
        board_id, {"action": "member_added", "member_id": add_user_id}
    )

    return {"message": "Member added successfully"}


@router.delete("/{board_id}/member")
async def delete_user_from_board(
    board_id: int,
    member_data: AddMember,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete one user using it id"""
    user_id = current_user.user_id

    # Is board → 404?
    board = db.query(Board).filter(Board.board_id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board is not found.")

    # Check the current user is owner of the board → 403
    # member_user_id is for deletion
    member_user_id = member_data.user_id

    is_owner = (
        db.query(BoardMembers)
        .filter(
            BoardMembers.board_id == board_id,
            BoardMembers.user_id == user_id,
            BoardMembers.role == "owner",
        )
        .first()
    )
    if not is_owner:
        raise HTTPException(
            status_code=403,
            detail="Only owner can delete members.",
        )

    # Deleted user is a member of the board → 404
    is_member = (
        db.query(BoardMembers)
        .filter(
            BoardMembers.board_id == board_id, BoardMembers.user_id == member_user_id
        )
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=404, detail="User is not a member of the board")

    # If I am an owner I can't delete myself → 400
    if is_owner.user_id == member_user_id:
        raise HTTPException(
            status_code=400, detail="You are an owner, deletion is forbidden."
        )

    db.delete(is_member)

    db.commit()

    await manager.publish(
        board_id, {"action": "member_deleted", "user_id": member_user_id}
    )

    return {
        "message": "Member is deleted",
    }


@router.patch("/{board_id}/transfer")
async def change_owner(
    board_id: int,
    member_data: AddMember,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Change board's owner"""
    # Get my and new one 's id
    current_user_id = current_user.user_id  # my id
    new_owner_id = member_data.user_id  # new owner's id

    # Does a board exist? → 404
    board = db.query(Board).filter(Board.board_id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board is not found")

    # Is current user an owner? → 403
    board_owner = (
        db.query(BoardMembers)
        .filter(
            BoardMembers.board_id == board_id,
            BoardMembers.user_id == current_user_id,
            BoardMembers.role == "owner",
        )
        .first()
    )
    if not board_owner:
        raise HTTPException(
            status_code=403, detail="Current user is not an owner of the board"
        )

    # Check if new member is taking a part in the board's team → 400
    board_member = (
        db.query(BoardMembers)
        .filter(
            BoardMembers.board_id == board_id,
            BoardMembers.user_id == new_owner_id,
            BoardMembers.role == "member",
        )
        .first()
    )

    if not board_member:
        raise HTTPException(
            status_code=400, detail="New one is not a member of the board's team"
        )

    # Change the current user's role on the member
    board_owner.role = "member"

    # Change the role of new owner
    board_member.role = "owner"

    db.commit()

    await manager.publish(
        board_id, {"action": "owner_changed", "new_owner_id": new_owner_id}
    )

    return {"message": "Role is changed"}


@router.get("/{board_id}/members", response_model=list[BoardMemberResponse])
def get_board_members(
    board_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get all members of a board"""
    user_id = current_user.user_id

    # Check current user is a member → 403
    is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="Access denied")

    members = (
        db.query(User.user_id, User.nickname, User.email, BoardMembers.role)
        .join(BoardMembers, BoardMembers.user_id == User.user_id)
        .filter(BoardMembers.board_id == board_id)
        .all()
    )

    return members


@router.patch("/{board_id}/color", response_model=BoardResponse)
async def update_board_color(
    board_id: int,
    color_data: BoardColorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update board color"""
    user_id = current_user.user_id

    board = db.query(Board).filter(Board.board_id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    is_member = (
        db.query(BoardMembers)
        .filter(BoardMembers.board_id == board_id, BoardMembers.user_id == user_id)
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="Access denied")

    board.color = color_data.color
    db.commit()
    db.refresh(board)

    await manager.publish(
        board_id, {"action": "board_color_changed", "color": board.color}
    )

    return BoardResponse.model_validate(board)
