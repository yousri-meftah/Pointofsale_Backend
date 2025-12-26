# **Project Description**
Point of Sale (POS) System: A user-friendly and efficient software solution designed for managing retail transactions. This project streamlines the checkout process by handling sales, inventory tracking, and customer management. Ideal for small to medium-sized retail businesses looking to enhance operational efficiency and improve customer service.


## **Overview**
This project is a backend service built with FastAPI, Docker, PostgreSQL, and Alembic for database migrations. The setup ensures seamless deployment and easy management with a `Makefile`.

---

## **Prerequisites**
Make sure the following tools are installed on your machine:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Make](https://www.gnu.org/software/make/)

---

## **Project Setup**

### 1. Clone the Repository
```bash
git clone https://github.com/yousri-meftah/Pointofsale_Backend.git
cd Pointofsale_Backend
```

### 2. Configure Environment Variables
Create and configure your environment variables in the `./envs/.env` and `./envs/postgres.env` files:



---

## **Makefile Commands**

The `Makefile` provides the following commands:

| Command         | Description                                       |
|-----------------|---------------------------------------------------|
| `make help`     | Show a list of available commands.                |
| `make build`    | Build the Docker images.                          |
| `make run`      | Run the Docker containers. Use `DETACHED=true` to run in detached mode. |
| `make deploy`   | Deploy the containers in detached mode.           |
| `make migrate`  | Run Alembic migrations to apply database changes. |
| `make admin`    | Create an admin user using the provided script.   |
| `make stop`     | Stop and remove the containers.                   |

---

## **How to Start the Project**

### 1. Build the Project
```bash
make build
```

### 2. Run the Project
```bash
make run
```

### 3. Run Database Migrations
```bash
make migrate
```

### 4. Create an Admin User
```bash
make admin
```

### 5. Stop the Project
```bash
make stop
```


