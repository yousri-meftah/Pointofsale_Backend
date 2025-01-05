import asyncio


from app.models import Employee,Employee_role
from app.enums import Role

from app.utils import hash_password
from core.database import get_db
from sqlalchemy.orm import Session



def create_admin_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    number: int,
    gender: str,
    status: str,
    contract_type: str,
    db: Session
):
    """
    Function to create an admin user in the employee table.
    """
    # Check if the user already exists by email (Unique constraint)


    # Hash the password
    hashed_password = hash_password(password)

    # Create a new Employee object with admin privileges
    new_admin = Employee(
        email=email,
        firstname=first_name,
        lastname=last_name,
        password=hashed_password,
        number=number,
        gender=gender,
        status=status,
        contract_type=contract_type,
        # You can set other fields like created_at or birthdate if needed
    )

    # Add and commit the new admin to the database
    db.add(new_admin)
    db.flush()
    employee_role = Employee_role(Employee_id=new_admin.id, role=Role.SUPER_USER)
    db.add(employee_role)
    #db.refresh(new_admin)
    db.commit()
    print(f"Admin {first_name} {last_name} created successfully.")
    return new_admin


def get_admin_input():
    """
    Get admin input from the command line.
    """
    email = input("Enter admin email: ")
    first_name = input("Enter admin first name: ")
    last_name = input("Enter admin last name: ")
    password = input("Enter admin password: ")
    number = int(input("Enter admin number: "))
    gender = input("Enter admin gender (e.g., MALE, FEMALE): ")
    status = input("Enter admin status (e.g., ACTIVE, INACTIVE): ")
    contract_type = input("Enter admin contract type (e.g., CDI, CDD): ")

    return email, first_name, last_name, password, number, gender, status, contract_type


async def main():
    email, first_name, last_name, password, number, gender, status, contract_type = get_admin_input()
    db_gen = get_db()
    db = next(db_gen)
    # Establish database connection and session

    create_admin_user(email, first_name, last_name, password, number, gender, status, contract_type, db)


if __name__ == "__main__":
    asyncio.run(main())
