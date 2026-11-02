from fastapi.testclient import TestClient
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app
from app import schemas
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Si no existe DATABASE_URL, armamos la URL usando settings (tu entorno local)
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

# 3. Solución al prefijo: Render entrega 'postgres://', pero SQLAlchemy requiere 'postgresql://'
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Crear el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear la fábrica de sesiones
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)



@pytest.fixture
def test_user2(client):
    user_data = {'email': 'panchito1234@gmail.com', 'password': 'password123'}

    res = client.post("/users/", json = user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def test_user(client):
    user_data = {'email': 'panchito123@gmail.com', 'password': 'password123'}

    res = client.post("/users/", json = user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [{ "title": "Test Post 1", "content": "This is a test post.", "owner_id": test_user['id'] },
                  { "title": "Test Post 2", "content": "This is another test post.", "owner_id": test_user['id'] },
                  { "title": "Test Post 3", "content": "Yet another test post.", "owner_id": test_user['id'] }]
    session.add_all([models.Post(title = "Test Post 1", content = "This is a test post.", owner_id = test_user['id']),
                     models.Post(title = "Test Post 2", content = "This is another test post.", owner_id = test_user['id']),
                     models.Post(title = "Test Post 3", content = "Yet another test post.", owner_id = test_user['id']),
                     models.Post(title = "Test Post 4", content = "This is a test post.", owner_id = test_user2['id'])])
    session.commit()

    posts = session.query(models.Post).all()

    return posts