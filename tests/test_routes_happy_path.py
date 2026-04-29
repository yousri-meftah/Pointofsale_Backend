from datetime import date, datetime, timedelta
from types import SimpleNamespace

from api.v1 import auth as auth_routes
from api.v1 import category as category_routes
from api.v1 import employee as employee_routes
from api.v1 import pricelist as pricelist_routes
from api.v1 import pricelist_line as pricelist_line_routes
from api.v1 import program as program_routes
from conftest import auth_headers, create_employee_with_roles, seed_catalog, seed_order, seed_session
from app.enums import Role, SessionStatusEnum
from app.models import Blacklist, Employee, PricelistLine


def test_auth_routes(client, monkeypatch):
    session = client.testing_session_local()
    user = create_employee_with_roles(session, "admin@example.com", [Role.ADMIN])
    client.auth_state.user = user

    async def fake_get_token(data, db):
        return {"access_token": "access", "refresh_token": "refresh", "expires_in": 1800}

    async def fake_get_refresh_token(token, db):
        return {"access_token": "new-access", "refresh_token": token, "expires_in": 1800}

    async def fake_activate(db, password, code):
        return True

    def fake_reset_password(db, code, password):
        return user

    async def fake_send_reset_password_email(email, db):
        return None

    monkeypatch.setattr(auth_routes, "get_token", fake_get_token)
    monkeypatch.setattr(auth_routes, "get_refresh_token", fake_get_refresh_token)
    monkeypatch.setattr(auth_routes, "activate_account_function", fake_activate)
    monkeypatch.setattr(auth_routes, "reset_password", fake_reset_password)
    monkeypatch.setattr(auth_routes, "send_reset_password_email", fake_send_reset_password_email)

    login_response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "Secret123!", "grant_type": "password"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"] == "access"

    refresh_response = client.post("/auth/refresh", headers={"refresh-token": "refresh-1"})
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"] == "new-access"

    logout_response = client.post("/auth/logout", headers=auth_headers())
    assert logout_response.status_code == 200
    assert session.query(Blacklist).count() == 1

    activate_response = client.post(
        "/auth/activate",
        json={"password": "Secret123!", "confirmPass": "Secret123!", "code": 111111},
    )
    assert activate_response.status_code == 200
    assert activate_response.json()["status"] == 200

    reset_response = client.post(
        "/auth/reset-password",
        json={"password": "Secret123!", "confirmPass": "Secret123!", "code": 222222},
    )
    assert reset_response.status_code == 200
    assert reset_response.json()["status"] == 200

    forgot_response = client.post("/auth/forget_password", json={"email": "admin@example.com"})
    assert forgot_response.status_code == 200
    assert forgot_response.json()["status"] == 200

    me_response = client.get("/auth/me", headers=auth_headers())
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "admin@example.com"


def test_category_routes(client, monkeypatch):
    session = client.testing_session_local()
    vendor = create_employee_with_roles(session, "vendor@example.com", [Role.VENDOR])
    client.auth_state.user = vendor

    async def fake_get_categories(db):
        return [{"id": 1, "name": "Beverages", "description": "Drinks", "icon_name": "cup"}]

    async def fake_create_category(db, category):
        return None

    async def fake_create_categories(categories, db):
        return [
            {"id": 1, "name": "Beverages", "description": "Drinks", "icon_name": "cup"},
            {"id": 2, "name": "Snacks", "description": "Food", "icon_name": "box"},
        ]

    async def fake_update_category(db, category_id, category):
        return {"id": category_id, "name": "Updated", "description": "Changed", "icon_name": "pen"}

    async def fake_delete_category(db, category_id):
        return {"id": 1, "name": "Beverages", "description": "Drinks", "icon_name": "cup"}

    monkeypatch.setattr(category_routes, "get_categories", fake_get_categories)
    monkeypatch.setattr(category_routes, "create_category", fake_create_category)
    monkeypatch.setattr(category_routes, "create_categories", fake_create_categories)
    monkeypatch.setattr(category_routes, "update_category", fake_update_category)
    monkeypatch.setattr(category_routes, "delete_category_by_name_or_id", fake_delete_category)

    assert client.get("/categories", headers=auth_headers()).status_code == 200
    assert client.post(
        "/categories",
        json={"name": "Beverages", "description": "Drinks", "icon_name": "cup"},
        headers=auth_headers(),
    ).json()["status"] == 201
    assert client.post(
        "/categories/add_categories",
        json=[
            {"name": "Beverages", "description": "Drinks", "icon_name": "cup"},
            {"name": "Snacks", "description": "Food", "icon_name": "box"},
        ],
        headers=auth_headers(),
    ).json()["status"] == 201
    assert client.patch(
        "/categories/1",
        json={"name": "Updated"},
        headers=auth_headers(),
    ).json()["status"] == 200
    assert client.delete("/categories/1", headers=auth_headers()).json()["status"] == 200


def test_customer_routes(client):
    session = client.testing_session_local()
    vendor = create_employee_with_roles(session, "vendor@example.com", [Role.VENDOR])
    client.auth_state.user = vendor
    _, pricelist, _, existing_customer = seed_catalog(session)

    list_response = client.get("/customers", headers=auth_headers())
    assert list_response.status_code == 200
    assert list_response.json()["total_records"] == 1

    get_response = client.get(f"/customers/{existing_customer.id}", headers=auth_headers())
    assert get_response.status_code == 200
    assert get_response.json()["email"] == existing_customer.email

    create_response = client.post(
        "/customers",
        json={"name": "Bob", "email": "bob@example.com", "pricelist_id": pricelist.id},
        headers=auth_headers(),
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == 201

    created_customer = session.query(Employee).filter_by(email="bob@example.com").first()
    assert created_customer is None

    customer_record = session.query(type(existing_customer)).filter_by(email="bob@example.com").first()
    update_response = client.put(
        f"/customers/{customer_record.id}",
        json={"name": "Bob Updated"},
        headers=auth_headers(),
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Bob Updated"

    delete_response = client.delete(f"/customers/{customer_record.id}", headers=auth_headers())
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == 200

    csv_content = "name,email,pricelist_id\nCSV User,csv@example.com,{0}\n".format(pricelist.id)
    bulk_response = client.post(
        "/customers/bulk_add",
        files={"file": ("customers.csv", csv_content, "text/csv")},
        headers=auth_headers(),
    )
    assert bulk_response.status_code == 200
    assert bulk_response.json()["status"] == "imported"


def test_dashboard_routes(client):
    session = client.testing_session_local()
    admin = create_employee_with_roles(session, "admin@example.com", [Role.ADMIN])
    client.auth_state.user = admin
    category, _, product, customer = seed_catalog(session)
    db_session = seed_session(session, admin.id, SessionStatusEnum.OPEN)
    seed_order(session, db_session.id, product.id, customer.id, total_price=20.0)

    revenue_response = client.get("/dashboard/revenue-per-category", headers=auth_headers())
    assert revenue_response.status_code == 200
    assert revenue_response.json()["sum"] == 20.0

    inventory_response = client.get("/dashboard/inventory-levels", headers=auth_headers())
    assert inventory_response.status_code == 200
    assert inventory_response.json()["total_inventory"] == product.quantity

    sales_response = client.get("/dashboard/sales-per-month", headers=auth_headers())
    assert sales_response.status_code == 200
    assert sales_response.json()["sales_per_month"]

    top_products_response = client.get(
        f"/dashboard/top-selling-products/{datetime.now().year}/{datetime.now().month}",
        headers=auth_headers(),
    )
    assert top_products_response.status_code == 200
    assert top_products_response.json()["top_selling_products"]

    earnings_response = client.get(
        f"/dashboard/monthly-earnings?year={datetime.now().year}",
        headers=auth_headers(),
    )
    assert earnings_response.status_code == 200
    assert "earnings_by_employee" in earnings_response.json()


def test_employee_routes(client, monkeypatch):
    session = client.testing_session_local()
    admin = create_employee_with_roles(session, "admin@example.com", [Role.ADMIN])
    target = create_employee_with_roles(session, "employee@example.com", [Role.VENDOR])
    client.auth_state.user = admin

    async def fake_create_employee(db, employee):
        return {"status": 201, "message": "Employee created successfully."}

    async def fake_create_from_csv(file, db):
        return {"successful": ["bulk@example.com"]}

    async def fake_update_employee(db, employee_id, employee_data):
        return SimpleNamespace(id=employee_id)

    monkeypatch.setattr(employee_routes, "create_employee", fake_create_employee)
    monkeypatch.setattr(employee_routes, "create_employees_from_csv", fake_create_from_csv)
    monkeypatch.setattr(employee_routes, "update_employee", fake_update_employee)
    monkeypatch.setattr(employee_routes, "discactivate_employee", lambda db, employee_id: True)

    list_response = client.get("/employee/get_all_employee", headers=auth_headers())
    assert list_response.status_code == 200
    assert list_response.json()["total_records"] >= 2

    get_response = client.get(f"/employee/{target.id}", headers=auth_headers())
    assert get_response.status_code == 200
    assert get_response.json()["email"] == target.email

    create_response = client.post(
        "/employee",
        json={
            "firstname": "New",
            "lastname": "Employee",
            "number": 9999,
            "gender": "MALE",
            "phone_number": "12345",
            "email": "new@example.com",
            "status": "ACTIVE",
            "birthdate": "2024-01-01",
            "contract_type": "CDI",
            "cnss_number": "12345678-90",
            "roles": [{"name": "VENDOR"}],
        },
        headers=auth_headers(),
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == 201

    csv_response = client.post(
        "/employee/csv",
        files={"file": ("employees.csv", "email,firstname\nx,y\n", "text/csv")},
        headers=auth_headers(),
    )
    assert csv_response.status_code == 200
    assert csv_response.json()["successful"] == ["bulk@example.com"]

    disactivate_response = client.patch(f"/employee/disactivate/{target.id}", headers=auth_headers())
    assert disactivate_response.status_code == 200
    assert disactivate_response.json() is True

    update_response = client.put(
        f"/employee/{target.id}",
        json={"firstname": "Updated"},
        headers=auth_headers(),
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == 200

    bulk_csv = (
        "email,firstname,lastname,number,gender,status,birthdate,contract_type,cnss_number,roles\n"
        "bulk1@example.com,Bulk,User,1234,MALE,ACTIVE,2024-01-01,CDI,12345678-90,VENDOR\n"
    )
    bulk_add_response = client.post(
        "/employee/bulk_add_employees",
        files={"file": ("bulk_employees.csv", bulk_csv, "text/csv")},
        headers=auth_headers(),
    )
    assert bulk_add_response.status_code == 200
    assert bulk_add_response.json()["status"] == "imported"


def test_order_routes(client):
    session = client.testing_session_local()
    vendor = create_employee_with_roles(session, "vendor@example.com", [Role.VENDOR])
    client.auth_state.user = vendor
    _, _, product, customer = seed_catalog(session)
    vendor_session = seed_session(session, vendor.id, SessionStatusEnum.OPEN)

    create_response = client.post(
        "/orders",
        json={
            "customer_id": customer.id,
            "products_ids": [[product.id, 2]],
            "session_id": vendor_session.id,
            "created_on": "2024-01-01T12:00:00",
            "total_price": 20.0,
            "pricelist_id": None,
            "program_item_id": None,
        },
        headers=auth_headers(),
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == 201

    list_response = client.get("/orders", headers=auth_headers())
    assert list_response.status_code == 200
    assert list_response.json()["total_records"] == 1

    order_id = list_response.json()["list"][0]["id"]
    details_response = client.get(f"/orders/orders/{order_id}/products", headers=auth_headers())
    assert details_response.status_code == 200
    assert details_response.json()["products"]


def test_pricelist_routes(client, monkeypatch):
    session = client.testing_session_local()
    vendor = create_employee_with_roles(session, "vendor@example.com", [Role.VENDOR])
    client.auth_state.user = vendor

    monkeypatch.setattr(
        pricelist_routes,
        "get_pricelists",
        lambda db: [SimpleNamespace(id=1, name="Default", description="Default prices")],
    )
    monkeypatch.setattr(
        pricelist_routes,
        "create_pricelist",
        lambda db, pricelist: SimpleNamespace(id=1, name=pricelist.name, description=pricelist.description),
    )
    monkeypatch.setattr(
        pricelist_routes,
        "update_pricelist",
        lambda db, pricelist_id, pricelist: SimpleNamespace(id=pricelist_id, name="Updated", description="Changed"),
    )
    monkeypatch.setattr(
        pricelist_routes,
        "get_all_pricelists_with_lines",
        lambda db: {1: [{"id": 1, "pricelist_id": 1, "product_name": "Coffee", "product_id": 1, "new_price": 8.0, "start_date": date(2024, 1, 1), "end_date": date(2024, 12, 31)}]},
    )
    monkeypatch.setattr(pricelist_routes, "delete_pricelistline", lambda pricelist_line_id, db: None)

    assert client.get("/pricelists", headers=auth_headers()).status_code == 200
    assert client.post(
        "/pricelists/pricelists",
        json={"name": "Default", "description": "Default prices"},
        headers=auth_headers(),
    ).json()["status"] == 201
    assert client.patch(
        "/pricelists/1",
        json={"name": "Updated"},
        headers=auth_headers(),
    ).json()["status"] == 200
    assert client.get("/pricelists/pricelists_with_lines", headers=auth_headers()).json()["status"] == 200
    assert client.delete("/pricelists/pricelist_line/1", headers=auth_headers()).json()["status"] == 200


def test_pricelist_line_routes(client, monkeypatch):
    session = client.testing_session_local()
    admin = create_employee_with_roles(session, "admin@example.com", [Role.ADMIN])
    client.auth_state.user = admin

    monkeypatch.setattr(
        pricelist_line_routes,
        "create_pricelist_line",
        lambda db, payload: SimpleNamespace(
            id=1,
            pricelist_id=payload.pricelist_id,
            product_id=payload.product_id,
            new_price=payload.new_price,
            start_date=payload.start_date,
            end_date=payload.end_date,
        ),
    )
    monkeypatch.setattr(
        pricelist_line_routes,
        "update_pricelist_line",
        lambda db, pricelist_line_id, payload: SimpleNamespace(
            id=pricelist_line_id,
            pricelist_id=1,
            product_id=payload.product_id or 1,
            new_price=payload.new_price or 7.5,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        ),
    )

    create_response = client.post(
        "/pricelist",
        json={"pricelist_id": 1, "product_id": 1, "new_price": 8.0, "start_date": "2024-01-01", "end_date": "2024-12-31"},
        headers=auth_headers(),
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == 201

    update_response = client.patch(
        "/pricelist/1",
        json={"product_id": 2, "new_price": 7.5},
        headers=auth_headers(),
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == 200


def test_product_routes(client):
    session = client.testing_session_local()
    inventory_user = create_employee_with_roles(session, "inventory@example.com", [Role.INVENTORY_MANAGER])
    client.auth_state.user = inventory_user
    category, pricelist, product, _ = seed_catalog(session)

    list_response = client.get("/products", headers=auth_headers())
    assert list_response.status_code == 200
    assert list_response.json()["total_records"] == 1

    create_response = client.post(
        "/products",
        json={
            "name": "Tea",
            "description": "Green tea",
            "unit_price": 5.0,
            "quantity": 25,
            "category_id": category.id,
        },
        headers=auth_headers(),
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == 201

    created_product = session.query(type(product)).filter_by(name="Tea").first()

    update_response = client.patch(
        f"/products/{created_product.id}",
        json={
            "name": "Tea Updated",
            "description": "Green tea",
            "unit_price": 6.0,
            "quantity": 30,
            "category_id": category.id,
        },
        headers=auth_headers(),
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == 200

    search_response = client.get("/products/search?name=Tea", headers=auth_headers())
    assert search_response.status_code == 200
    assert search_response.json()["products"]

    in_stock_response = client.get("/products/in-stock", headers=auth_headers())
    assert in_stock_response.status_code == 200

    created_product.quantity = 0
    session.add(created_product)
    session.commit()
    out_stock_response = client.get("/products/out-stock", headers=auth_headers())
    assert out_stock_response.status_code == 200
    assert any(item["id"] == created_product.id for item in out_stock_response.json()["products"])

    category_response = client.get(f"/products/category/{category.id}", headers=auth_headers())
    assert category_response.status_code == 200

    get_response = client.get(f"/products/{product.id}", headers=auth_headers())
    assert get_response.status_code == 200
    assert get_response.json()["products"][0]["id"] == product.id

    bulk_upload_response = client.post(
        "/products/bulk-upload",
        json=[
            {
                "name": "Water",
                "description": "Still water",
                "unit_price": 2.5,
                "quantity": 50,
                "category_id": category.id,
            }
        ],
        headers=auth_headers(),
    )
    assert bulk_upload_response.status_code == 200
    assert bulk_upload_response.json()["status"] == 201

    session.add(
        PricelistLine(
            pricelist_id=pricelist.id,
            product_id=product.id,
            new_price=8.0,
            min_quantity=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )
    )
    session.commit()

    pricelist_response = client.get(f"/products/pricelist/{pricelist.id}", headers=auth_headers())
    assert pricelist_response.status_code == 200

    bulk_delete_ids = [product.id, created_product.id]
    bulk_delete_response = client.request(
        "DELETE",
        "/products/bulk-delete",
        json=bulk_delete_ids,
        headers=auth_headers(),
    )
    assert bulk_delete_response.status_code == 200
    assert bulk_delete_response.json()["status"] == 200

    water_product = session.query(type(product)).filter_by(name="Water").first()
    delete_response = client.delete(f"/products/{water_product.id}", headers=auth_headers())
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == 200


def test_program_routes(client, monkeypatch):
    session = client.testing_session_local()
    admin = create_employee_with_roles(session, "admin@example.com", [Role.ADMIN])
    client.auth_state.user = admin

    async def fake_create_program(program, db):
        return None

    monkeypatch.setattr(program_routes, "create_program_with_items", fake_create_program)
    monkeypatch.setattr(
        program_routes,
        "get_all_program_items",
        lambda program_id, db: [{"id": 1, "code": "PROMO1", "status": "ACTIVE", "order_id": None}],
    )
    monkeypatch.setattr(
        program_routes,
        "calcul_program",
        lambda products, code, total, db: {"PROMO1": {"status": "VALID", "program_type": "DISCOUNT", "discount": 10.0}},
    )
    monkeypatch.setattr(
        program_routes,
        "get_BUTXGETY_program",
        lambda db: [{"id": 1, "code": "BUY1GET1", "status": "ACTIVE", "order_id": None, "discount": None, "product_buy_id": 1, "product_get_id": 2}],
    )
    monkeypatch.setattr(
        program_routes,
        "get_coupon_program",
        lambda db: [{"id": 2, "code": "DISC10", "status": "ACTIVE", "order_id": None, "discount": 10.0, "product_buy_id": None, "product_get_id": None}],
    )

    create_response = client.post(
        "/programs",
        json={
            "name": "Discount",
            "description": "Ten percent off",
            "program_type": "DISCOUNT",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "discount": 10.0,
            "product_buy_id": None,
            "product_get_id": None,
            "program_status": 1,
            "count": 10,
        },
        headers=auth_headers(),
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == 201

    items_response = client.get("/programs/1/items", headers=auth_headers())
    assert items_response.status_code == 200
    assert items_response.json()[0]["code"] == "PROMO1"

    calcule_response = client.post(
        "/programs/calcule_program",
        json={"code": ["PROMO1"], "total": 100.0, "products": [1, 2]},
        headers=auth_headers(),
    )
    assert calcule_response.status_code == 200
    assert calcule_response.json()["status"] == 200

    buyxgety_response = client.get("/programs/BUYXGETY_program", headers=auth_headers())
    assert buyxgety_response.status_code == 200
    assert buyxgety_response.json()["programs"]

    coupon_response = client.get("/programs/coupon_program", headers=auth_headers())
    assert coupon_response.status_code == 200
    assert coupon_response.json()["programs"]


def test_session_routes(client):
    session = client.testing_session_local()
    vendor = create_employee_with_roles(session, "vendor@example.com", [Role.VENDOR])
    client.auth_state.user = vendor

    create_response = client.post(
        "/sessions",
        json={
            "employee_id": vendor.id,
            "opened_at": "2024-01-01T10:00:00",
            "closed_at": "2024-01-01T18:00:00",
            "session_status": "OPEN",
        },
        headers=auth_headers(),
    )
    assert create_response.status_code == 200
    session_id = create_response.json()["Session_id"]

    list_response = client.get("/sessions", headers=auth_headers())
    assert list_response.status_code == 200
    assert list_response.json()["total_records"] == 1

    by_employee_response = client.get(f"/sessions/employee/{vendor.id}", headers=auth_headers())
    assert by_employee_response.status_code == 200
    assert by_employee_response.json()["total_records"] == 1

    opened_response = client.get("/sessions/opened_session", headers=auth_headers())
    assert opened_response.status_code == 200
    assert opened_response.json()["Session_id"] == session_id

    status_response = client.get(f"/sessions/{session_id}/status", headers=auth_headers())
    assert status_response.status_code == 200
    assert status_response.json()["session_status"] == "OPEN"

    pause_response = client.post(f"/sessions/{session_id}/pause", headers=auth_headers())
    assert pause_response.status_code == 200
    assert pause_response.json()["status"] == 200

    paused_response = client.get("/sessions/check_paused_session", headers=auth_headers())
    assert paused_response.status_code == 200
    assert paused_response.json()["Session_id"] == session_id

    resume_response = client.post(f"/sessions/{session_id}/resume", headers=auth_headers())
    assert resume_response.status_code == 200
    assert resume_response.json()["Session_id"] == session_id

    date_range_response = client.get(
        "/sessions/date_range?start_date=2023-12-31T00:00:00&end_date=2024-01-02T00:00:00",
        headers=auth_headers(),
    )
    assert date_range_response.status_code == 200
    assert date_range_response.json()["total_records"] == 1

    close_response = client.post(f"/sessions/{session_id}/close", headers=auth_headers())
    assert close_response.status_code == 200
    assert close_response.json()["status"] == 200

    second_session = seed_session(session, vendor.id, SessionStatusEnum.PAUSED)
    delete_response = client.delete(f"/sessions/{second_session.id}", headers=auth_headers())
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == 200
