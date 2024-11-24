from fastapi import status
from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_expired_after_time(client, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == status.HTTP_200_OK

        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'password': '123',
                'username': 'testusername',
                'email': 'test@test.com',
            },
        )

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        assert response.json() == {'detail': 'Method Not Allowed'}


def test_token_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_wrong_email(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'bla@bla.com', 'password': user.clean_password},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == status.HTTP_200_OK

        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.put(
            '/users/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        assert response.json() == {'detail': 'Method Not Allowed'}
