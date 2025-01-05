from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.token import get_current_user
from fastapi import HTTPException, status , Depends
from app.models.session import Session as SessionModel
from app.schemas.session import SessionCreate, SessionUpdate
from datetime import datetime
from app.models.employee import Employee
from app.enums import SessionStatusEnum
def get_sessions(db: Session, page_number: int, page_size: int):
    """ offset = (page - 1) * page_size
    products_query = db.query(ProductModel).offset(offset).limit(page_size)
    total_records = db.query(ProductModel).count()

    products = products_query.all()
    return products, total_records"""
    offset = (page_number - 1) * page_size
    query = db.query(SessionModel).offset(offset).limit(page_size)
    sessions = query.all()
    total_records = db.query(SessionModel).count()

    return sessions, total_records



def create_session(db: Session, session_data: SessionCreate):
    new_session = SessionModel(**session_data.dict())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


def update_session(db: Session, session_id: int, session_data: SessionUpdate):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    for key, value in session_data.dict(exclude_unset=True).items():
        setattr(session, key, value)
    db.commit()
    db.refresh(session)
    return session

def get_sessions_by_employee(db: Session,
    employee_id: int,
    page_number: int,
    page_size: int
    ):
    try:
        offset = (page_number - 1) * page_size
        query = db.query(SessionModel).filter(SessionModel.employee_id == employee_id).offset(offset).limit(page_size)
        sessions = query.all()
        total_records = db.query(func.count(SessionModel.id)).filter(SessionModel.employee_id == employee_id).scalar()
        return sessions, total_records
    except Exception as e:

        raise e



def close_session(
    db: Session, session_id: int, current_user: Employee = Depends(get_current_user)
):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session with ID {session_id} not found.")

    if session.employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this action.")

    session.session_status = SessionStatusEnum.CLOSED
    session.closed_at = datetime.now()

    db.commit()
    return session

def pause_session(
    db: Session, session_id: int, current_user: Employee = Depends(get_current_user)
):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session with ID {session_id} not found.")

    if session.employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this action.")

    session.session_status = SessionStatusEnum.PAUSED

    db.commit()


def resume_session(
    db: Session, session_id: int, current_user: Employee
):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session with ID {session_id} not found.")

    if session.employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this action.")


    session.session_status = SessionStatusEnum.OPEN

    db.commit()
    return session


def delete_session_by_id(
    db: Session, session_id: int, current_user: Employee
):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session with ID {session_id} not found.")

    if session.employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to perform this action.")

    db.delete(session)
    db.commit()


def get_sessions_with_date_range(db: Session, start_date: datetime, end_date: datetime, page: int, page_size: int):
    offset = (page - 1) * page_size
    sessions_query = db.query(SessionModel).filter(
        SessionModel.opened_at >= start_date,
        SessionModel.opened_at <= end_date
    )
    total_records = sessions_query.count()
    sessions = sessions_query.offset(offset).limit(page_size).all()
    return sessions, total_records