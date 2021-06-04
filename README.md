# Secret Santa Service

This is a microservice designed for managing a family "Secret Santa."  This project utilizes FastAPI as a web framework, SQLite to store data, and SQLalchemy for ORM.
  
## Installation

There's a pipfile and a requirements.txt,  do what works best for you.  

I wrote this using python 3.8.  I'm unsure if anything in this project is new to 3.8, but figured I'd give you a heads up.

## Usage

once all requirements have been met,  cd into the directory and run:

```
uvicorn main:app --reload
```

Once the service is running,  go ahead and visit http://localhost:8000/docs in your browser for endpoint documentation.  

After you've added a few records(at least 5) and run the gift exchange a few times,  feel free to visit the root page(http://localhost:8000/) in a web browser to get a visual on the DB structure. The DB design isn't my best work, but I'd trust it enough to use with my own family.  

Feel free to take a look at the test file(test.py), and when you're ready just run it.

It'll generate a test DB, load in some dummy names, hit all the endpoints, and then call the gift exchange endpoint 1000 times(1000 years).  

## Closing Statement

Things I could have done better:  FastAPI has a good bit of built-in http error responses built-in,  but its not perfect. So I could have spent some more time thinking of test cases with regard to how someone could misuse the API(as they do), and then create responses that properly handle that misuse.

All of that said, I'm fairly happy with this project, not only how it turned out, but also the odd challenges it presented along the way.  It was a fun time.  

If you have any questions, feel free to reach out.  

-B
