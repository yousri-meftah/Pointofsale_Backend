from main import app


EXPECTED_APP_ROUTES = {
    ("GET", "/auth/me"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("POST", "/auth/logout"),
    ("POST", "/auth/activate"),
    ("POST", "/auth/reset-password"),
    ("POST", "/auth/forget_password"),
    ("GET", "/employee/get_all_employee"),
    ("GET", "/employee/{employee_id}"),
    ("POST", "/employee"),
    ("POST", "/employee/csv"),
    ("PATCH", "/employee/disactivate/{employee_id}"),
    ("PUT", "/employee/{employee_id}"),
    ("POST", "/employee/bulk_add_employees"),
    ("GET", "/products"),
    ("POST", "/products"),
    ("PATCH", "/products/{product_id}"),
    ("GET", "/products/search"),
    ("GET", "/products/in-stock"),
    ("GET", "/products/out-stock"),
    ("DELETE", "/products/bulk-delete"),
    ("GET", "/products/{product_id}"),
    ("GET", "/products/category/{category_id}"),
    ("POST", "/products/bulk-upload"),
    ("DELETE", "/products/{product_id}"),
    ("GET", "/products/pricelist/{pricelist_id}"),
    ("GET", "/dashboard/revenue-per-category"),
    ("GET", "/dashboard/inventory-levels"),
    ("GET", "/dashboard/sales-per-month"),
    ("GET", "/dashboard/top-selling-products/{year}/{month}"),
    ("GET", "/dashboard/monthly-earnings"),
    ("GET", "/categories"),
    ("POST", "/categories"),
    ("POST", "/categories/add_categories"),
    ("PATCH", "/categories/{category_id}"),
    ("DELETE", "/categories/{id}"),
    ("POST", "/programs"),
    ("GET", "/programs/{program_id}/items"),
    ("POST", "/programs/calcule_program"),
    ("GET", "/programs/BUYXGETY_program"),
    ("GET", "/programs/coupon_program"),
    ("GET", "/sessions"),
    ("POST", "/sessions"),
    ("GET", "/sessions/employee/{employee_id}"),
    ("POST", "/sessions/{session_id}/close"),
    ("POST", "/sessions/{session_id}/pause"),
    ("POST", "/sessions/{session_id}/resume"),
    ("GET", "/sessions/date_range"),
    ("DELETE", "/sessions/{session_id}"),
    ("GET", "/sessions/opened_session"),
    ("GET", "/sessions/check_paused_session"),
    ("GET", "/sessions/{session_id}/status"),
    ("GET", "/orders"),
    ("POST", "/orders"),
    ("GET", "/orders/orders/{order_id}/products"),
    ("GET", "/customers"),
    ("GET", "/customers/{id}"),
    ("POST", "/customers"),
    ("PUT", "/customers/{customer_id}"),
    ("DELETE", "/customers/{customer_id}"),
    ("POST", "/customers/bulk_add"),
    ("GET", "/pricelists"),
    ("POST", "/pricelists/pricelists"),
    ("PATCH", "/pricelists/{pricelist_id}"),
    ("GET", "/pricelists/pricelists_with_lines"),
    ("DELETE", "/pricelists/pricelist_line/{pricelist_line_id}"),
    ("POST", "/pricelist"),
    ("PATCH", "/pricelist/{pricelist_line_id}"),
}


def test_all_included_backend_routes_are_accounted_for():
    actual_routes = {
        (method, route.path)
        for route in app.routes
        if hasattr(route, "methods")
        for method in route.methods
        if method not in {"HEAD", "OPTIONS"} and route.path not in {"/", "/openapi.json", "/redoc", "/docs/oauth2-redirect"}
    }

    assert actual_routes == EXPECTED_APP_ROUTES
