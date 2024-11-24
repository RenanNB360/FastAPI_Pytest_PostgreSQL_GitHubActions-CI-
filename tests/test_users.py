from fastapi import status

from fast_postgres.schema import UserPublic


def test_create_user_should_return_405_username_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {'detail': 'Method Not Allowed'}


def test_create_user_should_return_405_email_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': user.email,
            'password': 'secret',
        },
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {'detail': 'Method Not Allowed'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testusername',
            'email': 'test@test.com',
            'password': 'password',
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.json() == {
        'username': 'testusername',
        'email': 'test@test.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == status.HTTP_202_ACCEPTED

    assert response.json() == {'users': []}


def test_put_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'password': '123',
            'username': 'testusername',
            'email': 'test@test.com',
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert response.json() == {'detail': 'Not enough permission'}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'password': '123',
            'username': 'testusername',
            'email': 'test@test.com',
        },
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        'username': 'testusername',
        'email': 'test@test.com',
        'id': user.id,
    }


def test_delete_wrong_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert response.json() == {'detail': 'Not enough permission'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {'message': 'User Deleted'}


def test_get_user_not_found(client):
    response = client.get('/users/777')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {'detail': 'Not Found'}


def test_read_user(client):
    client.post(
        '/users/',
        json={
            'username': 'testusername',
            'email': 'test@test.com',
            'password': 'password',
        },
    )

    response = client.get('/users/1')

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        'username': 'testusername',
        'email': 'test@test.com',
        'id': 1,
    }


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.status_code == status.HTTP_202_ACCEPTED

    assert response.json() == {'users': [user_schema]}
