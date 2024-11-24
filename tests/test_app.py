from fastapi import status


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act (ação)

    assert response.status_code == status.HTTP_200_OK  # Assert
    assert response.json() == {'message': 'Olá Mundo!'}
