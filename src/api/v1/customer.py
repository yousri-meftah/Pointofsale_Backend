from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session as DBSession
from app.schemas.base import OurBaseModelOut
from app.schemas.customer import Customer, CustomerOut ,CustomerCreate,CustomerUpdate,CustomersOut,CustomerOut_withstatus,BulkAddResponse
from app.controllers.customer import  create_customer, update_customer,list_customers,delete_customer,bulk_create_customers,customer_by_id
from fastapi import File, UploadFile, HTTPException
import csv
import io
from redis.asyncio import Redis
import json
from app.models.customer import Customer as CustomerModel
from app.enums import Role
from core.database import get_db
from app.services.token import oauth2_scheme, RoleChecker
from app.models.pricelist import Pricelist
from app.utils import map_fields
from core.redis import get_redis
from sqlalchemy.exc import IntegrityError



from datetime import datetime
from sqlalchemy.orm import class_mapper

def model_to_dict(obj):
    """Convert SQLAlchemy model instance to a dictionary, handling complex types."""
    serialized_data = {}

    for column in class_mapper(obj.__class__).columns:
        value = getattr(obj, column.key)

        if isinstance(value, datetime):
            # Convert datetime objects to string
            serialized_data[column.key] = value.isoformat()
        else:
            # For other types, just store the value directly
            serialized_data[column.key] = value

    return serialized_data


expected_fields = {
    'name': 'name',
    'email': 'email',
    'pricelist_id': 'pricelist_id'
}

allow_action_by_roles = RoleChecker([Role.SUPER_USER, Role.ADMIN , Role.VENDOR])

router = APIRouter(
    dependencies=[Depends(oauth2_scheme) , Depends(allow_action_by_roles)]
)

@router.get("/", response_model=CustomersOut)
def list_customers_route(
    db: DBSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    try:
        customers, total_records = list_customers(db, page, page_size)
        total_pages = (total_records + page_size - 1) // page_size

        return CustomersOut(
            status=status.HTTP_200_OK,
            message="Customers retrieved successfully.",
            list=customers,
            page_number=page,
            page_size=page_size,
            total_pages=total_pages,
            total_records=total_records
        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving customers."
        )


"""@router.get("/", response_model=CustomersOut)
async def list_customers_route(
    db: DBSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    cache_key = f"customers:page:{page}:page_size:{page_size}"

    try:
        cached_data = await redis.get(cache_key)

        if cached_data:
            print("cache hit")
            customers_data = json.loads(cached_data)
            return CustomersOut(**customers_data)
        print("cache miss")
        customers, total_records = list_customers(db, page, page_size)
        total_pages = (total_records + page_size - 1) // page_size
        print
        customers_dict = [model_to_dict(customer) for customer in customers]
        response_data = {
            "status": status.HTTP_200_OK,
            "message": "Customers retrieved successfully.",
            "list": customers_dict,
            "page_number": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_records": total_records
        }

        # Cache the data in Redis
        await redis.set(cache_key, json.dumps(response_data), ex=3600)  # Cache for 1 hour

        return CustomersOut(**response_data)

    except Exception as e:
        print("e = ",e)
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving customers."
        )"""



@router.get("/{id}", response_model=CustomerOut_withstatus)
def list_customers_route(
    id:int,
    db: DBSession = Depends(get_db),
):
    try:
        customer = customer_by_id(db,id)

        return CustomerOut_withstatus(
            status=status.HTTP_200_OK,
            message="get customer by id succes .",
            **customer.__dict__

        )
    except Exception as e:
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while retrieving customers."
        )

@router.post("/", response_model=CustomerOut_withstatus)
def create_customer_route(
    customer: CustomerCreate,
    db: DBSession = Depends(get_db),
):
    try:
        new_customer = create_customer(db, customer)

        return CustomerOut_withstatus(
            status=status.HTTP_201_CREATED,
            message="Customer created successfully.",
            **new_customer.__dict__
        )
    except Exception as e:
        db.rollback()
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating the customer."
        )

@router.put("/{customer_id}", response_model=CustomerOut_withstatus)
def update_customer_route(
    customer_id: int,
    customer: CustomerUpdate,
    db: DBSession = Depends(get_db),
):
    try:
        updated_customer = update_customer(db, customer_id, customer)
        return CustomerOut_withstatus(
            status=status.HTTP_200_OK,
            message="Customer updated successfully.",
            **updated_customer.__dict__
        )
    except HTTPException as e:
        db.rollback()
        return OurBaseModelOut(
            status=e.status_code,
            message=e.detail
        )
    except Exception as e:
        db.rollback()
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating the customer."
        )

@router.delete("/{customer_id}", response_model=OurBaseModelOut)
def delete_customer_route(
    customer_id: int,
    db: DBSession = Depends(get_db),
):
    try:
        delete_customer(db, customer_id)
        return OurBaseModelOut(
            status=status.HTTP_200_OK,
            message="Customer deleted successfully."
        )
    except Exception as e:
        db.rollback()
        return OurBaseModelOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while deleting the customer."
        )


#@router.post("/bulk_add", response_model=BulkAddResponse)
async def bulk_add_customers(
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
):
    if file.content_type != 'text/csv':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a CSV file."
        )

    content = await file.read()
    csv_reader = csv.DictReader(io.StringIO(content.decode('utf-8')))

    # Map the headers
    headers = csv_reader.fieldnames
    field_mapping = map_fields(headers,expected_fields)

    errors = []
    valid_customers = []

    for line_number, row in enumerate(csv_reader, start=1):
        try:
            # Map the row fields according to the field_mapping
            mapped_row = {field_mapping[key]: value for key, value in row.items()}

            # Validate pricelist_id
            pricelist_id = mapped_row.get('pricelist_id')
            if pricelist_id:
                pricelist = db.query(Pricelist).filter(Pricelist.id == pricelist_id).first()
                if not pricelist:
                    raise ValueError(f"Pricelist ID {pricelist_id} does not exist.")

            # Check if email already exists
            email = mapped_row['email']
            existing_customer = db.query(CustomerModel).filter(CustomerModel.email == email).first()
            if existing_customer:
                raise ValueError(f"Email {email} already exists in the database.")

            customer_data = CustomerCreate(
                name=mapped_row['name'],
                email=mapped_row['email'],
                pricelist_id=pricelist_id if pricelist_id else None
            )
            valid_customers.append(customer_data)
        except Exception as e:
            errors.append({"line": str(line_number), "error": str(e)})

    if errors:
        return BulkAddResponse(
            status=status.HTTP_400_BAD_REQUEST,
            message="Errors found in the CSV file.",
            errors=errors
        )

    try:
        added_customers = await bulk_create_customers(db, valid_customers)
        return BulkAddResponse(
            status=status.HTTP_201_CREATED,
            message="Customers added successfully.",
            added_customers=added_customers
        )
    except Exception as e:
        return BulkAddResponse(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while adding customers."
        )
    

@router.post("/bulk_add")
async def bulk_add_customers(
    force : bool =False ,
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db)
):
    # Check if the uploaded file is a CSV
    if file.content_type != 'text/csv':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a CSV file."
        )

    # Read the CSV content
    content = await file.read()
    csv_reader = csv.DictReader(io.StringIO(content.decode('utf-8')))

    # Initialize containers for validation
    data = []
    can_force_errors = []
    critical_errors = []
    valid_customers = []

    for line_number, row in enumerate(csv_reader, start=1):
        email = row.get("email", "").strip()
        name = row.get("name", None)
        pricelist_id = row.get("pricelist_id", None)
        data.append(row)
        # Check if email is empty
        if not email:
            critical_errors.append({"line": line_number, "error": "Email is a required field."})
            continue

        # Check if email already exists in the database
        if db.query(CustomerModel).filter(CustomerModel.email == email).first():
            critical_errors.append({"line": line_number, "error": f"Email {email} already exists."})
            continue

        # Validate pricelist_id if provided
        if pricelist_id :
            pricelist = db.query(Pricelist).filter(Pricelist.id == pricelist_id).first()
            if not pricelist and not force:
                can_force_errors.append(f"Line {line_number}: Pricelist ID {pricelist_id} does not exist , It will be null if you force ")
                pricelist_id = None
            elif force:
                pricelist_id = None


        if (name == ''or name==None) and not force:
            can_force_errors.append(f"line {line_number}: name {name} does not have a value , It will be null if you force ")
        # Add customer to the valid list
        valid_customers.append(CustomerModel(
            email=email,
            name=name if name else None,
            pricelist_id=int(pricelist_id) if pricelist_id else None
        ))

    # Check for errors and return appropriate response
    if critical_errors:
        return {
            "status": "error",
            "errors": critical_errors,
            "can_force": can_force_errors,
            "data": data,
        }

    # If there are no critical errors, allow force import or proceed to store the file
    if can_force_errors:
        return {
            "status": "can_force",
            "errors": [],
            "can_force": can_force_errors,
            "data": data,
        }

    # Save valid customers to the database
    try:
        db.add_all(valid_customers)
        db.commit()
        return {
            "status": "imported",
            "message": f"Successfully imported {len(valid_customers)} customers."
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )