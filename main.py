import random, itertools, models
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from models import family_member, recipient_record


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


class NameRequest(BaseModel):
    name: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


response404 = "Item not found"


@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    """
    Returns a page which displays all tables.
    """
    family_members = db.query(family_member).all()
    recipient_records = db.query(recipient_record).all()
    response = templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "family_members": family_members,
            "recipient_records": recipient_records,
        },
    )
    return response


@app.get("/members")
async def get_all_family_members(db: Session = Depends(get_db)):
    """
    Returns a list of all family members.
    """
    family_member_db_entries = db.query(family_member).all()
    try:
        response = [
            {"id": str(entry.id), "name": entry.first_name}
            for entry in family_member_db_entries
        ]
    except AttributeError:
        raise HTTPException(status_code=404, detail=response404)
    return response


@app.get("/members/{id}")
async def get_family_member_by_id(id: int, db: Session = Depends(get_db)):
    """
    Returns a single family member by ID.
    """
    try:
        family_member_db_entry = (
            db.query(family_member).filter(family_member.id == id).first()
        )

        response = {
            "id": str(family_member_db_entry.id),
            "name": family_member_db_entry.first_name,
        }
    except AttributeError:
        raise HTTPException(status_code=404, detail=response404)
    return response


@app.post("/members")
async def add_family_member(name_request: NameRequest, db: Session = Depends(get_db)):
    """
    Adds a family member to the database.
    """

    # Instantiate and send to DB
    new_family_member = family_member()
    new_family_member.first_name = name_request.name
    db.add(new_family_member)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Bad request, likely due to this name already existing in the database.")
    #print("you are lost")

    # Confirm placement in DB and query its ID
    family_member_db_entry = (
        db.query(family_member)
        .filter(family_member.first_name == name_request.name)
        .first()
    )
    try:
        response = {
            "id": str(family_member_db_entry.id),
            "name": family_member_db_entry.first_name,
        }
    except AttributeError:
        raise HTTPException(status_code=404, detail=response404)
    return response


@app.put("/members/{id}")
async def update_family_member_by_id(
    id: int, name_request: NameRequest, db: Session = Depends(get_db)
):
    """
    Updates a single family member's name by ID.
    """
    try:
        family_member_db_entry = (
            db.query(family_member).filter(family_member.id == id).first()
        )

        old_name = family_member_db_entry.first_name
        family_member_db_entry.first_name = name_request.name
        db.commit()

        response = {"id": str(id), "old_name": old_name, "name": name_request.name}

    except AttributeError:
        raise HTTPException(status_code=404, detail=response404)

    return response


@app.delete("/members/{id}")
async def delete_family_member_by_id(id: int, db: Session = Depends(get_db)):
    """
    Deletes a single family member by ID.
    """

    family_member_db_entry = (
        db.query(family_member).filter(family_member.id == id).first()
    )
    if family_member_db_entry:
        db.delete(family_member_db_entry)
        db.commit()
        response = {
            "id": str(family_member_db_entry.id),
            "name": family_member_db_entry.first_name,
            "deleted": True,
        }
        return response
    else:
        raise HTTPException(status_code=404, detail=response404)


@app.get("/gift_exchange")
async def gift_exchange(db: Session = Depends(get_db)):
    """
    Shuffles family members and then iterates backwards through the list to give pairings.

    Will reshuffle and try again if one of its entries are found in the last 3 years.
    """

    # Retrive past 3 years of gift exchange pairings.
    records = db.query(recipient_record).all()
    records = [record.record for record in records[-3:]]
    # merge each year's records into one list
    records = list(itertools.chain.from_iterable(records))
    # Retreive all family member IDs as a list, then make a copty of that list.

    family_member_db_entries = db.query(family_member).all()
    if len(family_member_db_entries)<5:
        raise HTTPException(status_code=409, detail="Unable to process request due to not enough members of the family in the database. This is why Grandma keeps bothering me to have kids.")

    family_ids = [entry.id for entry in family_member_db_entries]

    # I know this line isnt necessary, but my IDE was complaining.  Don't judge me.
    assignmentlist = []

    match_found = False
    while match_found == False:

        random.shuffle(family_ids)
        
        # reverse index transversal works better here due to limitations in
        # how python handles positive indexes/indices.
        assignmentlist = [
            {"member_id": str(uid), "recipient_member_id": str(family_ids[index - 1])}
            for index, uid in enumerate(family_ids)
        ]

        # Check against previous years of pairings
        if [i for i in assignmentlist if i in records]:
            continue

        else:
            match_found = True

    assignments = recipient_record()
    assignments.record = assignmentlist
    db.add(assignments)
    db.commit()

    return assignmentlist