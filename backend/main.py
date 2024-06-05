from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from starlette.middleware.sessions import SessionMiddleware




app = FastAPI()

# Set up CORS
origins = [
    "*",  # Replace with your actual frontend origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="123")

DATABASE = './db.db'  # Replace with your actual database file


class Administrateur(BaseModel):
    Nom: str
    Prenom: str
    Email: str
    MotDePasse: str

from typing import Optional

class Utilisateur(BaseModel):
    NomU: str
    NomPrenomU: str
    email: str
    MdpU: str
    Tel: str
    AdrU: str

class AnnonceBien(BaseModel):
    IdAn: int
    Tit: str
    Descr: str
    AdrA: str
    Surf: str
    Prix: int
    StatA: str
    Img: str
    IdU: int
    IdCom: int
    IdCat: int

class Reservation(BaseModel):
    DateDebut: str
    DateFin: str
    IdU: int
    IdAB: int

class Catégorie(BaseModel):
    Nom: str




def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/wilayas")
async def get_wilayas():
    conn = get_db_connection()
    wilayas = conn.execute('SELECT * FROM Wilaya').fetchall()
    conn.close()
    return JSONResponse([dict(ix) for ix in wilayas])

@app.get("/api/communes")
async def get_communes(wilaya_id: int = Query(None, description="ID of the Wilaya to filter communes")):
    conn = get_db_connection()
    if wilaya_id is not None:
        communes = conn.execute('SELECT * FROM Commune WHERE IdWi = ?', (wilaya_id,)).fetchall()
        conn.close()
        if not communes:
            raise HTTPException(status_code=404, detail="No communes found for this wilaya_id")
        return JSONResponse([dict(ix) for ix in communes])
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="wilaya_id is required")


@app.post("/annoncebien/")
async def create_annoncebien(IdAn: int = Form(...), Tit: str = Form(...), Descr: str = Form(...), AdrA: str = Form(...), Surf: str = Form(...), Prix: int = Form(...), StatA: str = Form(...), Img: str = Form(...), IdU: int = Form(...), IdCom: int = Form(...), IdCat: int = Form(...)):
    annoncebien = AnnonceBien(IdAn=IdAn, Tit=Tit, Descr=Descr, AdrA=AdrA, Surf=Surf, Prix=Prix, StatA=StatA, Img=Img, IdU=IdU, IdCom=IdCom, IdCat=IdCat)
    
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO AnnonceBien (IdAn, Tit, Descr, AdrA, Surf, Prix, StatA, Img, IdU, IdCom, IdCat) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (annoncebien.IdAn, annoncebien.Tit, annoncebien.Descr, annoncebien.AdrA, annoncebien.Surf, annoncebien.Prix, annoncebien.StatA, annoncebien.Img, annoncebien.IdU, annoncebien.IdCom, annoncebien.IdCat)
    )
    conn.commit()
    conn.close()

    return {"message": "AnnonceBien created successfully"}

@app.post("/utilisateur/")
async def create_utilisateur(NomU: str = Form(...), NomPrenomU: str = Form(...), email: str = Form(...), MdpU: str = Form(...), Tel: str = Form(...), AdrU: str = Form(...)):
    utilisateur = Utilisateur(NomU=NomU, NomPrenomU=NomPrenomU, email=email, MdpU=MdpU, Tel=Tel, AdrU=AdrU)
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO Utilisateur (NomU,MdpU,email,NomPrenomU,Tel,AdrU)  values (?,?,?,?,?,?)",
        (utilisateur.NomU,utilisateur.MdpU,utilisateur.email,utilisateur.NomPrenomU,utilisateur.Tel,utilisateur.AdrU)
    )
    return RedirectResponse(url='/login.html', status_code=303)

@app.post("/annoncebien/")
async def create_annoncebien(annoncebien: AnnonceBien):
    conn = get_db_connection()
    conn.execute('INSERT INTO AnnonceBien (Titre, Description, Prix, IdU) VALUES (?, ?, ?, ?)',
                 (annoncebien.Titre, annoncebien.Description, annoncebien.Prix, annoncebien.IdU))
    conn.commit()
    conn.close()
    return JSONResponse({"message": "AnnonceBien created successfully"})

@app.post("/reservation/")
async def create_reservation(reservation: Reservation):
    conn = get_db_connection()
    conn.execute('INSERT INTO Réservation (DateDebut, DateFin, IdU, IdAB) VALUES (?, ?, ?, ?)',
                 (reservation.DateDebut, reservation.DateFin, reservation.IdU, reservation.IdAB))
    conn.commit()
    conn.close()
    return JSONResponse({"message": "Réservation created successfully"})

@app.post("/categorie/")
async def create_categorie(categorie: Catégorie):
    conn = get_db_connection()
    conn.execute('INSERT INTO Catégorie (Nom) VALUES (?)',
                 (categorie.Nom,))
    conn.commit()
    conn.close()
    return JSONResponse({"message": "Catégorie created successfully"})

@app.get("/annoncebien/")
async def get_annoncebiens():
    conn = get_db_connection()
    annoncebiens = conn.execute('SELECT * FROM AnnonceBien').fetchall()
    conn.close()
    return JSONResponse([dict(ix) for ix in annoncebiens])

@app.post("/login/")
async def login(request: Request, email: str = Form(...), MdpU: str = Form(...)):
    conn = get_db_connection()
    utilisateur = conn.execute('SELECT * FROM Utilisateur WHERE email = ? AND MdpU = ?', (email, MdpU)).fetchone()
    conn.close()
    if utilisateur:
        request.session["utilisateur"] = dict(utilisateur)
        return RedirectResponse(url='/index.html', status_code=303)
    else:
        return RedirectResponse(url='/login.html', status_code=303)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
