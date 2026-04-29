import pytest

from app.enums import Role, SessionStatusEnum
from conftest import auth_headers, create_employee_with_roles, seed_catalog, seed_order, seed_session


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("get", "/auth/me", None),
        ("post", "/auth/logout", None),
        ("get", "/employee/get_all_employee", None),
        ("get", "/categories", None),
        ("get", "/customers", None),
        ("get", "/dashboard/revenue-per-category", None),
        ("get", "/orders", None),
        ("get", "/products", None),
        ("get", "/pricelists", None),
        ("post", "/pricelist", {"pricelist_id": 1, "product_id": 1, "new_price": 8.0, "start_date": "2024-01-01", "end_date": "2024-12-31"}),
        ("get", "/programs/coupon_program", None),
        ("get", "/sessions", None),
    ],
)
def test_protected_endpoints_require_authentication(client, method, path, json_body):
    request_kwargs = {}
    if json_body is not None:
        request_kwargs["json"] = json_body
    response = getattr(client, method)(path, **request_kwargs)
    assert response.status_code == 401


def test_employee_endpoints_forbid_vendor_role(client):
    session = client.testing_session_local()
    vendor = create_employee_with_roles(session, "vendor@example.com", [Role.VENDOR])
    client.auth_state.user = vendor

    response = client.get("/employee/get_all_employee", headers=auth_headers())

    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not permitted"


def test_dashboard_endpoints_forbid_vendor_role(client):
    session = client.testing_session_local()
    vendor = create_employee_with_roles(session, "vendor@example.com", [Role.VENDOR])
    client.auth_state.user = vendor

    response = client.get("/dashboard/revenue-per-category", headers=auth_headers())

    assert response.status_code == 403


def test_order_endpoints_forbid_inventory_manager_role(client):
    session = client.testing_session_local()
    inventory_user = create_employee_with_roles(session, "inventory@example.com", [Role.INVENTORY_MANAGER])
    client.auth_state.user = inventory_user

    response = client.get("/orders", headers=auth_headers())

    assert response.status_code == 403


def test_product_write_endpoints_allow_inventory_manager_and_forbid_vendor(client):
    session = client.testing_session_local()
    category, _, _, _ = seed_catalog(session)
    vendor = create_employee_with_roles(session, "vendor@example.com", [Role.VENDOR])
    inventory_user = create_employee_with_roles(session, "inventory@example.com", [Role.INVENTORY_MANAGER])

    product_payload = {
        "name": "Tea",
        "description": "Green tea",
        "unit_price": 5.5,
        "quantity": 10,
        "category_id": category.id,
    }

    client.auth_state.user = vendor
    forbidden_response = client.post("/products", json=product_payload, headers=auth_headers())
    assert forbidden_response.status_code == 403

    client.auth_state.user = inventory_user
    allowed_response = client.post("/products", json=product_payload, headers=auth_headers())
    assert allowed_response.status_code == 200
    assert allowed_response.json()["status"] == 201


def test_product_delete_is_now_role_protected(client):
    session = client.testing_session_local()
    _, _, product, _ = seed_catalog(session)
    vendor = create_employee_with_roles(session, "vendor@example.com", [Role.VENDOR])
    inventory_user = create_employee_with_roles(session, "inventory@example.com", [Role.INVENTORY_MANAGER])

    client.auth_state.user = vendor
    forbidden_response = client.delete(f"/products/{product.id}", headers=auth_headers())
    assert forbidden_response.status_code == 403

    client.auth_state.user = inventory_user
    allowed_response = client.delete(f"/products/{product.id}", headers=auth_headers())
    assert allowed_response.status_code == 200
    assert allowed_response.json()["status"] == 200


def test_session_create_for_other_employee_returns_403(client):
    session = client.testing_session_local()
    owner = create_employee_with_roles(session, "owner@example.com", [Role.VENDOR])
    other = create_employee_with_roles(session, "other@example.com", [Role.VENDOR])
    client.auth_state.user = owner

    payload = {
        "employee_id": other.id,
        "opened_at": "2024-01-01T10:00:00",
        "closed_at": "2024-01-01T18:00:00",
        "session_status": "OPEN",
    }

    response = client.post("/sessions", json=payload, headers=auth_headers())

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("path_builder", "expected_status"),
    [
        (lambda s: f"/sessions/{s.id}/close", 403),
        (lambda s: f"/sessions/{s.id}/pause", 403),
        (lambda s: f"/sessions/{s.id}/resume", 403),
        (lambda s: f"/sessions/{s.id}", 403),
    ],
)
def test_session_owner_operations_reject_other_users(client, path_builder, expected_status):
    session = client.testing_session_local()
    owner = create_employee_with_roles(session, "owner@example.com", [Role.VENDOR])
    intruder = create_employee_with_roles(session, "intruder@example.com", [Role.VENDOR])
    owner_session = seed_session(session, owner.id, SessionStatusEnum.OPEN)
    client.auth_state.user = intruder

    path = path_builder(owner_session)
    if path.endswith("/close") or path.endswith("/pause") or path.endswith("/resume"):
        response = client.post(path, headers=auth_headers())
    else:
        response = client.delete(path, headers=auth_headers())

    assert response.status_code == expected_status


def test_vendor_cannot_create_order_for_another_users_session(client):
    session = client.testing_session_local()
    _, _, product, customer = seed_catalog(session)
    owner = create_employee_with_roles(session, "owner@example.com", [Role.VENDOR])
    other = create_employee_with_roles(session, "other@example.com", [Role.VENDOR])
    other_session = seed_session(session, other.id, SessionStatusEnum.OPEN)
    client.auth_state.user = owner

    payload = {
        "customer_id": customer.id,
        "products_ids": [[product.id, 1]],
        "session_id": other_session.id,
        "created_on": "2024-01-01T12:00:00",
        "total_price": 10.0,
        "pricelist_id": None,
        "program_item_id": None,
    }

    response = client.post("/orders", json=payload, headers=auth_headers())

    assert response.status_code == 403


def test_vendor_only_sees_their_own_orders(client):
    session = client.testing_session_local()
    _, _, product, customer = seed_catalog(session)
    owner = create_employee_with_roles(session, "owner@example.com", [Role.VENDOR])
    other = create_employee_with_roles(session, "other@example.com", [Role.VENDOR])
    owner_session = seed_session(session, owner.id, SessionStatusEnum.OPEN)
    other_session = seed_session(session, other.id, SessionStatusEnum.OPEN)
    seed_order(session, owner_session.id, product.id, customer.id)
    seed_order(session, other_session.id, product.id, customer.id)
    client.auth_state.user = owner

    response = client.get("/orders", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["total_records"] == 1
    assert len(response.json()["list"]) == 1
    assert response.json()["list"][0]["session_id"] == owner_session.id


def test_vendor_cannot_view_order_from_another_users_session(client):
    session = client.testing_session_local()
    _, _, product, customer = seed_catalog(session)
    owner = create_employee_with_roles(session, "owner@example.com", [Role.VENDOR])
    other = create_employee_with_roles(session, "other@example.com", [Role.VENDOR])
    other_session = seed_session(session, other.id, SessionStatusEnum.OPEN)
    foreign_order = seed_order(session, other_session.id, product.id, customer.id)
    client.auth_state.user = owner

    response = client.get(f"/orders/orders/{foreign_order.id}/products", headers=auth_headers())

    assert response.status_code == 403
