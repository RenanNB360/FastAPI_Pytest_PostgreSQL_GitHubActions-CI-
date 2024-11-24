from sqlalchemy import select

from fast_postgres.models import User


def test_create_user(session):
    user = User(
        username='renan', email='renan@hotmail.com', password='minha_senha'
    )

    session.add(user)
    session.commit()

    result = session.scalar(
        select(User).where(User.email == 'renan@hotmail.com')
    )

    assert result.username == 'renan'
