from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlmodel import select

from models.db.user_role import ADMIN_USER_NAME, DEFAULT_ROLE_NAME, Role, User
from models.permissions import Permission
from utils.security import gen_pwd_hash

from settings import settings


def init_user_role(session: Session):
    admin_user = session.scalar(select(User).where(User.name == ADMIN_USER_NAME))
    if not admin_user:
        admin_user = User(
            name=ADMIN_USER_NAME,
            phone_num="-",
            pwd_hash=gen_pwd_hash(settings.ADMIN_PWD),
            is_admin=True,
        )
        session.add(admin_user)
    default_role = session.scalar(select(Role).where(Role.name == DEFAULT_ROLE_NAME))
    if not admin_user:
        default_role = Role(name=DEFAULT_ROLE_NAME, permissions=Permission(0))
        session.add(default_role)
    session.commit()


def init():
    engine = create_engine(
        str(settings.POSTGRES_DB_URI_SYNC),
        echo=settings.DATABASE_ECHO,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
    )
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    with SessionLocal() as session:
        init_user_role(session)
