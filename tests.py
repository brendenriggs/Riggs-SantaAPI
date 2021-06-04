from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from main import app, get_db
from tqdm import tqdm
import os


"""
Hi there,  welcome to my test file.  Admittedly,  I'm still learning how to create comprehensive tests, 
however this file ended up being fairly useful in generating dummy data and 
validating that any changes didn't break expected behavior. 
"""


# Removes existing test.b, if applicable
if os.path.exists("test.db"):
    os.remove("test.db")

# Creates a test.db so we don't interfere with prod data while testing.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Dummy list of friend and pet names to populate the db.
family = [
    "Brenden",
    "Carol Ann",
    "D'Andre",
    "Pippin",
    "Bear",
    "Mack",
    "Dan",
    "Lara",
    "Sameera",
    "Piper",
    "Kyle",
    "Robbie",
    "Jazz",
    "Eric",
]


def test_add_family_member(name):
    """
    Adds a family member, then does a get request
    to confirm that they're in the DB
    """
    response = client.post("/members", json={"name": f"{name}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == f"{name}"
    assert "id" in data

    # Uses response from creating entry to build next request
    uid = data["id"]
    response = client.get(f"/members/{uid}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == f"{name}"
    assert data["id"] == uid
    return True


def test_get_all_family_members(family):
    """
    Gets all family members from DB, then verifies that
    those entries match the family list.
    """
    response = client.get("/members")
    assert response.status_code == 200, response.text
    data = response.json()
    names = [entry["name"] for entry in data]
    assert names == family
    return True


def test_update_family_member_by_id(uid, name):
    """
    Gets current name by uid,  the sends update request.
    Verifies expected response against request and old name.
    """
    old_name = client.get(f"/members/{uid}").json()["name"]
    response = client.put(f"/members/{uid}", json={"name": name})
    assert response.json() == {"id": str(uid), "old_name": old_name, "name": name}
    return True


def test_delete_family_member_by_id(uid):
    """
    Verifies existence of an entry by ID,  then deletes it,
    then verifies that the entry is no longer accessible.
    """
    assert client.get(f"/members/{uid}").status_code == 200
    client.delete(f"/members/{uid}")
    assert client.get(f"/members/{uid}").status_code == 404
    return True



def test_gift_exchange():
    """
    Runs the gift exchange, then verifies valid pairings
    """
    response = client.get(f"/gift_exchange")
    assert response.status_code == 200
    entries = [entry for entry in response.json()]
    for entry in entries:
        assert entry["member_id"] != entry["recipient_member_id"]
    return True


def test_all_tests(family):
    """
    Since some tests can only run if theres data in the DB,
    I wrote this function which will run all tests in a logical order.
    """
    print("Running all tests:")
    # populate with dummy data and verify addition to db
    for name in family:
        test_add_family_member(name)

    # get list of all family members
    test_get_all_family_members(family)

    # modify someones name
    test_update_family_member_by_id(14, "John")

    # delete an entry
    test_delete_family_member_by_id(13)

    # run the gift exchange 1000 times
    for i in tqdm(range(1000)):
        test_gift_exchange()
    print("Test Complete!")


test_all_tests(family)
