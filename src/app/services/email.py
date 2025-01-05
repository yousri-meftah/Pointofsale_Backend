import datetime
from fastapi_mail import MessageSchema, FastMail, MessageType,ConnectionConfig
from sqlalchemy.orm import Session
from core.config import settings
from app.models import Blacklist,Activation_account,Change_password,Employee
from app.schemas.employee import User as Create_employee
import secrets
from app.enums import Token_status
from pathlib import Path
from app.enums import Token_status




templates_path = Path(__file__).parent.parent.parent / 'templates'

if not templates_path.is_dir():
    raise ValueError("The TEMPLATE_FOLDER path does not point to a directory." , templates_path)


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    USE_CREDENTIALS=True,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=templates_path
)

def generate_random_number(digits):
    return int(''.join(secrets.choice('0123456789') for _ in range(digits)))

async def send_reset_password_email(email: str, db: Session):
    employee = db.query(Employee).filter(Employee.email == email).first()
    jwt = generate_random_number(6)
    expire_minutes = int(settings.JWT_EXPIRATION_MINUETS)
    expiry_date = datetime.datetime.now() + datetime.timedelta(minutes=expire_minutes)
    token = Change_password( Employee_id =employee.id ,token=jwt, created_at=expiry_date , status = Token_status.PENDING)
    db.add(token)



    link = "http://localhost:3000/reset-password/" + str(jwt)

    message = MessageSchema(
            subject="Reset Your Password",
            recipients=[employee.email],
            template_body={"firstname": employee.firstname, "lastname": employee.lastname, "link": link},
            subtype=MessageType.html)
    template_name = "reset_password.html"

    fm = FastMail(conf)
    #await fm.send_message(message, template_name=template_name)
    db.commit()



async def send_activation_email(employee: Create_employee, db: Session):
    jwt = generate_random_number(6)
    expire_minutes = int(settings.JWT_EXPIRATION_MINUETS)
    expiry_date = datetime.datetime.now() + datetime.timedelta(minutes=expire_minutes)
    token = Activation_account( Employee_id =employee.id ,token=jwt, created_at=expiry_date , status = Token_status.PENDING)
    db.add(token)

    link = "http://localhost:3000/activate/" + str(jwt)
    message = MessageSchema(
        subject="Activate your account",
        recipients=[employee.email],
        template_body={"firstname": employee.firstname, "lastname": employee.lastname, "link": link},
        subtype=MessageType.html)
    template_name = "email_template.html"

    fm = FastMail(conf)
    #await fm.send_message(message, template_name=template_name)
    db.flush()