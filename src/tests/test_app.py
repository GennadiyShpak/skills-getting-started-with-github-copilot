import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

# use the TestClient provided by FastAPI
@pytest.fixture

def client():
    return TestClient(app_module.app)

# reset activities for each test by using a deep copy of the original
@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    # restore after test
    app_module.activities = original


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    # should match the initial dictionary structure
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Gym Class" in data


def test_successful_signup(client):
    email = "new@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    # verify internal state changed
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate(client):
    email = "michael@mergington.edu"  # already in participants
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_nonexistent_activity(client):
    response = client.post("/activities/NoSuch/signup?email=test@example.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success(client):
    email = "daniel@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_remove_participant_nonexistent_activity(client):
    response = client.delete("/activities/Nope/participants?email=x@x.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_not_signed_up(client):
    email = "absent@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
