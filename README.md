# The RTS Bibtex Database

This database maintains the citations and papers for the Real-Time Systems Group 
at the Univeristy of York. It was developed because the University-wide
system, [PURE](https://www.york.ac.uk/staff/research/pure/), doesn't allow us to store the papers alongside the citations. 
PURE also does not allow organisation by research group.

The database is implemented as a Django application, and is currently
deployed on a VPS, `csvps13`, provided by CS Support. The main departmental web server
proxies requests to `www.cs.york.ac.uk/rts/bibtex/*` through to here.

When deploying, a secret key must be generated in the file `csbibtex/settings_secret.py` as:

```python
SECRET_KEY = 'thisisanexamplesecret'
```

Also an sqlite database will need to be created at `db/db.sqlite3`.

## Important note on security
When deployed, the database is protected by the [ITSAccess](https://www.cs.york.ac.uk/support/itsaccess/) 
Apache module, which sets the `REMOTE_USER` environment variable and ensures that only University 
staff can access it. Therefore, this code should not be considered safe for the general internet.