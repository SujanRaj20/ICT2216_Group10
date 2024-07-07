import pytest
from flask import url_for

# def test_true():
#     assert True
    
# def test_false():
#     assert False
    

@pytest.mark.parametrize('endpoint', ['/'])
def test_route_exists(client, endpoint):
    response = client.get(endpoint)
    assert response.status_code == 200

def test_non_existing_route(client):
    response = client.get('/non_existing_route')
    assert response.status_code == 404
    
    