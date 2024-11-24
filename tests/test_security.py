from fastapi import status
from jwt import decode

from fast_postgres.security import create_access_token, settings


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)

    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert result['exp']


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {'detail': 'Method Not Allowed'}


def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {'detail': 'Method Not Allowed'}


def test_get_current_user_does_not_exists(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {'detail': 'Method Not Allowed'}
