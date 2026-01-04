from fastapi import FastAPI
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