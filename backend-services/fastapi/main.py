from fastapi import FastAPI, Path, Query, HTTPException
import json
app = FastAPI()

def data_loader():
    with open("patients.json", "r") as file:
        data = json.load(file)
    return data

@app.get("/")
def intro():
    return {"message": "Welcome to the Patient Management API!"}

@app.get("/about")
def about():
    return {"message": "This API provides information about patients."}

@app.get("/view")
def view_patients():
    patients = data_loader()
    return {"patients": patients}

@app.get("/view/{patient_id}")
def view_patient(patient_id: str = Path(..., description="ID of the patient", example="P001")):
    data = data_loader()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404, detail="Patient not found")