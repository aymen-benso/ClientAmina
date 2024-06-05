from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi.requests import Request




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

DATABASE = './db.db'  # Replace with your actual database file


class Administrateur(BaseModel):
    Nom: str
    Prenom: str
    Email: str
    MotDePasse: str

from typing import Optional

class Utilisateur(BaseModel):
    IdU: Optional[int] = None
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
    IdAn: int

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
    print(utilisateur)

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO Utilisateur (NomU, MdpU, email, NomPrenomU,Tel,AdrU)  VALUES (?, ?, ?, ?, ?, ?)",
        (utilisateur.NomU,utilisateur.MdpU,utilisateur.email,utilisateur.NomPrenomU,utilisateur.Tel,utilisateur.AdrU)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url='http://127.0.0.1:5500/login.html', status_code=303)


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
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO Réservation1 (DateDebut, DateFin, IdU, IdAn) VALUES (?, ?, ?, ?)',
                     (reservation.DateDebut, reservation.DateFin, reservation.IdU, reservation.IdAn))
        conn.commit()
        conn.close()
        return JSONResponse({"message": "Réservation created successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)

@app.get("/mesreservations/")
async def get_mesreservations(IdU: int = Query(None, description="ID of the User to filter reservations")):
    conn = get_db_connection()
    if IdU is not None:
        reservations = conn.execute('SELECT * FROM Réservation1 WHERE IdU = ?', (IdU,)).fetchall()
        conn.close()
        if not reservations:
            raise HTTPException(status_code=404, detail="No reservations found for this IdU")
        return JSONResponse([dict(ix) for ix in reservations])
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="IdU is required")

@app.post("/categorie/")
async def create_categorie(categorie: Catégorie):
    conn = get_db_connection()
    conn.execute('INSERT INTO Catégorie (Nom) VALUES (?)',
                 (categorie.Nom,))
    conn.commit()
    conn.close()
    return JSONResponse({"message": "Catégorie created successfully"})



@app.post("/login/")
async def login(request: Request, email: str = Form(...), MdpU: str = Form(...)):
    conn = get_db_connection()
    utilisateur = conn.execute('SELECT * FROM Utilisateur WHERE email = ? AND MdpU = ?', (email, MdpU)).fetchone()
    print(utilisateur)
    conn.close()
    if utilisateur:
        utilisateur = dict(utilisateur)
        return JSONResponse({"message": "Login successful" , "user": utilisateur}, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/annoncebien/")
async def get_annoncebiens():
    conn = get_db_connection()
    annoncebiens = conn.execute('SELECT * FROM AnnonceBien').fetchall()
    conn.close()
    return JSONResponse([dict(ix) for ix in annoncebiens])

@app.post("/lesutilisateurs/")
async def get_lesutilisateurs():
    conn = get_db_connection()
    lesutilisateurs = conn.execute('SELECT * FROM Utilisateur').fetchall()
    conn.close()
    return JSONResponse([dict(ix) for ix in lesutilisateurs])

@app.post("/supprimerutilisateur/")
async def supprimer_utilisateur(IdU: int = Form(...)):
    conn = get_db_connection()
    conn.execute('DELETE FROM Utilisateur WHERE IdU = ?', (IdU,))
    conn.commit()
    conn.close()
    return JSONResponse({"message": "Utilisateur supprimé avec succès"})

@app.post("/supprimerannonce/")
async def supprimer_annonce(IdAn: int = Form(...)):
    conn = get_db_connection()
    conn.execute('DELETE FROM AnnonceBien WHERE IdAn = ?', (IdAn,))
    conn.commit()
    conn.close()
    return JSONResponse({"message": "Annonce supprimée avec succès"})



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
