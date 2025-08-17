import json
from http import HTTPStatus
from faker import Faker
import pytest
import requests
from app.models.User import User


@pytest.fixture(scope="module")
def fill_test_data(app_url):
    with open("users.json") as f:
        test_data_users = json.load(f)
    api_users = []
    for user in test_data_users:
        response = requests.post(f"{app_url}/api/users/", json=user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")


@pytest.fixture()
def random_user():
    fake = Faker("ru_RU")
    return {
        "last_name": fake.last_name(),
        "first_name": fake.first_name(),
        "email": fake.ascii_free_email(),
        "avatar": "https://reqres.in/img/faces/8-image.jpg"
    }


@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()


@pytest.mark.usefixtures("fill_test_data")
def test_users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK

    user_list = response.json()
    for user in user_list:
        User.model_validate(user)


@pytest.mark.usefixtures("fill_test_data")
def test_users_no_duplicates(users):
    users_ids = [user["id"] for user in users]
    assert len(users_ids) == len(set(users_ids))


def test_user(app_url, fill_test_data):
    for user_id in (fill_test_data[0], fill_test_data[-1]):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK
        user = response.json()
        User.model_validate(user)


@pytest.mark.parametrize("user_id", [13])
def test_user_nonexistent_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_user_invalid_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_post_user(app_url, random_user):
    post_response = requests.post(f"{app_url}/api/users", json=random_user)
    assert post_response.status_code == HTTPStatus.CREATED
    new_user = post_response.json()
    id = new_user["id"]
    get_response = requests.get(f"{app_url}/api/users/{id}")
    assert get_response.json()["last_name"] == random_user["last_name"]
    assert get_response.json()["first_name"] == random_user["first_name"]
    assert get_response.json()["email"] == random_user["email"]
    assert get_response.json()["avatar"] == random_user["avatar"]
    requests.delete(f"{app_url}/api/users/{id}")


def test_delete_user(app_url, random_user):
    id = requests.post(f"{app_url}/api/users", json=random_user).json()["id"]
    delete_response = requests.delete(f"{app_url}/api/users/{id}")
    assert delete_response.status_code == HTTPStatus.OK
    get_response = requests.get(f"{app_url}/api/users/{id}")
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_patch_user(app_url, random_user):
    post_response = requests.post(f"{app_url}/api/users", json=random_user)
    new_user = post_response.json()
    id = new_user["id"]
    random_user["first_name"] = Faker().first_name()
    patch_response = requests.patch(f"{app_url}/api/users/{id}", json=random_user)
    assert patch_response.status_code == HTTPStatus.OK

    patched_user = requests.get(f"{app_url}/api/users/{id}").json()
    assert patched_user["last_name"] == random_user["last_name"]
    assert patched_user["first_name"] == random_user["first_name"]
    assert patched_user["email"] == random_user["email"]
    assert patched_user["avatar"] == random_user["avatar"]

    requests.delete(f"{app_url}/api/users/{id}")


def test_not_allowed_method(app_url):
    delete = requests.delete(f"{app_url}/api/users/")
    assert delete.status_code == HTTPStatus.METHOD_NOT_ALLOWED
