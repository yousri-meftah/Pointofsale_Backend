import os
import sys
from datetime import date, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


os.environ.setdefault("POSTGRES_URL", "sqlite:///./bootstrap.db")
os.environ.setdefault("MAIL_USERNAME", "test@example.com")
os.environ.setdefault("MAIL_PASSWORD", "password")
os.environ.setdefault("MAIL_FROM", "test@example.com")
os.environ.setdefault("MAIL_PORT", "1025")
os.environ.setdefault("MAIL_SERVER", "localhost")
os.environ.setdefault("MAIL_FROM_NAME", "POS Test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_MINUETS", "30")
os.environ.setdefault("CODE_EXPIRATION_MINUTES", "30")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


import core.database as core_database
from app.enums import AccountStatus, ContractType, Gender, Role, SessionStatusEnum
from app.models import Base, Category, Customer, Employee, Employee_role, Order, OrderLine, Pricelist, Product, Session
from app.services.token import get_current_user
from core.database import get_db
from main import app


class AuthState:
    user = None


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(core_database, "SessionLocal", testing_session_local)
    monkeypatch.setattr(core_database, "engine", engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    auth_state = AuthState()
    auth_state.user = None

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    def override_current_user():
        if auth_state.user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return auth_state.user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as test_client:
        test_client.auth_state = auth_state
        test_client.testing_session_local = testing_session_local
        yield test_client

    app.dependency_overrides.clear()


def auth_headers():
    return {"Authorization": "Bearer test-token"}


def create_employee_with_roles(session, email: str, roles: list[Role]):
    employee = Employee(
        firstname="Test",
        lastname=email.split("@")[0],
        password="hashed-password",
        number=12345,
        gender=Gender.MALE,
        status=AccountStatus.ACTIVE,
        email=email,
        birthdate=date(2024, 1, 1),
        contract_type=ContractType.CDI,
        cnss_number="12345678-90",
    )
    session.add(employee)
    session.flush()
    for role in roles:
        session.add(Employee_role(Employee_id=employee.id, role=role))
    session.commit()
    session.refresh(employee)
    return employee


def seed_catalog(session):
    category = Category(name="Beverages", description="Drinks", icon_name="cup")
    pricelist = Pricelist(name="Default", description="Default prices")
    session.add_all([category, pricelist])
    session.flush()

    product = Product(
        name="Coffee",
        description="Hot coffee",
        unit_price=10.0,
        quantity=50,
        category_id=category.id,
    )
    customer = Customer(name="Alice", email="alice@example.com", pricelist_id=pricelist.id)
    session.add_all([product, customer])
    session.commit()
    session.refresh(category)
    session.refresh(pricelist)
    session.refresh(product)
    session.refresh(customer)
    return category, pricelist, product, customer


def seed_session(session, employee_id: int, status: SessionStatusEnum = SessionStatusEnum.OPEN):
    db_session = Session(
        employee_id=employee_id,
        opened_at=datetime(2024, 1, 1, 10, 0, 0),
        closed_at=datetime(2024, 1, 1, 18, 0, 0),
        session_status=status,
    )
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session


def seed_order(session, session_id: int, product_id: int, customer_id: int | None = None, total_price: float = 20.0):
    order = Order(
        number="1",
        customer_id=customer_id,
        session_id=session_id,
        total_price=total_price,
    )
    session.add(order)
    session.flush()
    order_line = OrderLine(
        order_id=order.id,
        product_id=product_id,
        unit_price=10.0,
        quantity=2,
        total_price=20.0,
    )
    session.add(order_line)
    session.commit()
    session.refresh(order)
    return order
