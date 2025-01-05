from fastapi import APIRouter, Depends, HTTPException, status,Query,Path
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from datetime import datetime
from app.schemas.session import Session, SessionOut , SessionsOut,SessionCreateOut,check_status
from app.controllers.session import get_sessions, create_session, update_session , get_sessions_by_employee , close_session,\
    pause_session,resume_session, get_sessions_with_date_range,delete_session_by_id

from app.models.employee import Employee
from app.enums import SessionStatusEnum
from app.models.session import Session as SessionModel
from app.services.token import get_current_user
from app.enums import Role
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker

allow_action_by_roles = RoleChecker([Role.SUPER_USER, Role.VENDOR])

router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)


@router.get("/", response_model=SessionsOut)
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    db: DBSession = Depends(get_db),
):
    try:
        sessions, total_records =  get_sessions(db, page, page_size)
        total_pages = (total_records + page_size - 1) // page_size  # Calculate total pages
        return SessionsOut(
            status=status.HTTP_200_OK,
            message="Sessions retrieved successfully.",
            page_number=page,
            page_size=page_size,
            total_pages=total_pages,
            total_records=total_records,
            list=sessions
        )

    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving sessions."
        )

@router.post("/", response_model=SessionCreateOut)
async def create_session_endpoint(session: Session, db: DBSession = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    try:
        if session.employee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a session for this employee."
            )

        employee = db.query(Employee).filter(Employee.id == session.employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found."
            )
        open_session = db.query(SessionModel).filter(SessionModel.session_status == SessionStatusEnum.OPEN ).first()
        paused_session = db.query(SessionModel).filter(SessionModel.session_status == SessionStatusEnum.PAUSED ).first()
        if open_session or paused_session:
            return OurBaseModelOut(
            status=status.HTTP_400_BAD_REQUEST,
            message="There is already an open or paused session."
        )

        new_session = create_session(db, session )
        return SessionCreateOut(
            status=status.HTTP_201_CREATED,
            message="Session created successfully.",
            Session_id=new_session.id
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating session."
        )

#@router.patch("/{session_id}", response_model=OurBaseModelOut)
async def update_session_endpoint(session_id: int, session: Session, db: DBSession = Depends(get_db)):
    try:
        updated_session = update_session(db, session_id, session)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Session updated successfully.",
            data=updated_session
        )
    except HTTPException as e:
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating session."
        )


@router.get("/employee/{employee_id}", response_model=SessionsOut)
async def get_sessions_by_employee_id(
    employee_id: int,
    page_number: int = Query(1, description="Page number, starting from 1"),
    page_size: int = Query(10, description="Number of items per page"),
    db: DBSession = Depends(get_db),
):
    try:
        sessions, total_records = get_sessions_by_employee(db, employee_id, page_number, page_size)
        total_pages = (total_records + page_size - 1) // page_size

        return SessionsOut(
            status=status.HTTP_200_OK,
            message="Sessions retrieved successfully.",
            list=sessions,
            page_number=page_number,
            page_size=page_size,
            total_pages=total_pages,
            total_records=total_records
        )
    except Exception as e:
        return SessionsOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving sessions.",
            list=None
        )




@router.post("/{session_id}/close", response_model=SessionOut)
async def close_a_session(session_id: int, db: DBSession = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    try:
        session = close_session(db, session_id, current_user)
        return SessionOut(
            status=status.HTTP_200_OK,
            message="Session closed successfully.",
            employee_id=session.employee_id,
            opened_at=session.opened_at,
            closed_at=session.closed_at,
            session_status=session.session_status
        )
    except HTTPException as e:
        return HTTPException(
            status_code=e.status_code,
            detail=str(e.detail)
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while closing the session."
        )



@router.post("/{session_id}/pause", response_model=OurBaseModelOut)
async def pausee_session(session_id: int, db: DBSession = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    try:
        pause_session(db, session_id, current_user)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Session paused successfully."
        )
    except HTTPException as e:
        return HTTPException(
            status_code=e.status_code,
            detail=str(e.detail)
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while pausing the session."
        )


@router.post("/{session_id}/resume", response_model=SessionCreateOut)
async def resume_session_endpoint(
    session_id: int = Path(..., title="The ID of the session to resume"),
    db: DBSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    try:
        sess = resume_session(db, session_id , current_user)
        return SessionCreateOut(
            status=status.HTTP_200_OK,
            message=f"Session {session_id} resumed successfully.",
            Session_id=sess.id

        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to resume session {session_id}."
        )

@router.get("/date_range", response_model=SessionsOut)
async def get_sessions_by_date_range(
    start_date: datetime = Query(..., title="Start date of the range"),
    end_date: datetime = Query(..., title="End date of the range"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    db: DBSession = Depends(get_db),
):
    try:
        sessions, total_records = get_sessions_with_date_range(db, start_date, end_date, page, page_size)
        total_pages = (total_records + page_size - 1) // page_size
        return SessionsOut(
            status=status.HTTP_200_OK,
            message="Sessions retrieved successfully.",
            page_number=page,
            page_size=page_size,
            total_pages=total_pages,
            total_records=total_records,
            list=sessions
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sessions for date range: {start_date} to {end_date}."
        )


@router.delete("/{session_id}", response_model=OurBaseModelOut)
async def delete_session(
    session_id: int = Path(..., title="The ID of the session to delete"),
    db: DBSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    try:
        delete_session_by_id(db, session_id , current_user)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message=f"Session {session_id} deleted successfully."
        )
    except HTTPException as e:
        return HTTPException(
            status_code=e.status_code,
            detail=str(e.detail)
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to delete session {session_id}."
        )


@router.get("/opened_session" , response_model=SessionCreateOut)
def opened_session(db : DBSession = Depends(get_db) ,current_user: Employee = Depends(get_current_user)):
    try:
        session = db.query(SessionModel).filter(SessionModel.employee_id == current_user.id).filter(SessionModel.session_status == SessionStatusEnum.OPEN).first()
        if session is None:
            return OurBaseModelOut(
                status=status.HTTP_404_NOT_FOUND,
                message=f"No opened session found for employee with ID {current_user.id}."
            )

        return SessionCreateOut(
            status=status.HTTP_200_OK,
            message="Opened session retrieved successfully.",
            Session_id=session.id
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An error occurred while retrieving the opened session."
        )

@router.get("/check_paused_session/" , response_model=SessionCreateOut)
def opened_session(db : DBSession = Depends(get_db),current_user: Employee = Depends(get_current_user) ):
    try:
        session = db.query(SessionModel).filter(SessionModel.employee_id == current_user.id).filter(SessionModel.session_status == SessionStatusEnum.PAUSED).first()
        if session is None:
            return OurBaseModelOut(
                status=status.HTTP_404_NOT_FOUND,
                message=f"No opened session found for employee with ID {current_user.id}."
            )

        return SessionCreateOut(
            status=status.HTTP_200_OK,
            message="Opened session retrieved successfully.",
            Session_id=session.id
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An error occurred while retrieving the opened session."
        )

@router.get("/{session_id}/status", response_model=check_status)
async def check_session_status(
    session_id: int = Path(..., title="The ID of the session to check"),
    db: Session = Depends(get_db)
):
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found."
            )

        return check_status(
            status = status.HTTP_200_OK,
            message = "Session status retrieved successfully.",
            session_status = session.session_status.name

        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An error occurred while checking the session status. Error: {str(e)}"
        )