from fastapi import FastAPI, Path, Query, HTTPException
import json
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Optional, Annotated

app = FastAPI()

class Patient(BaseModel):
    name: Annotated[str, Field(description="Full name of the patient", example="Jabbar Khan")]
    city: Annotated[str, Field(description="City of residence", example="Islamabad")]
    age: Annotated[int, Field(description="Age of the patient", example=30)]
    gender: Annotated[Literal["male", "female", "other"], Field(description="Gender of the patient", example="male")]
    height: Annotated[float, Field(description="Height of the patient in centimeters", example=175.5)]
    weight: Annotated[float, Field(description="Weight of the patient in kilograms", example=70.2)]

    @computed_field
    @property
    def id(self) -> str:
        data = data_loader()
        id = list(data.keys())[-1]
        id_number = str.split(id, "P")[-1]
        new_id_number = int(id_number) + 1
        if new_id_number < 10:
            new_id = "P00" + str(new_id_number)
        elif 10 <= new_id_number < 100:
            new_id = "P0" + str(new_id_number)
        else:
            new_id = "P" + str(new_id_number)
        return new_id    
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = self.weight / ((self.height / 100) ** 2)
        return round(bmi, 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal weight"
        elif 25 <= bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"

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


@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="Sort by height, weight, or bmi", example="height"), order: str = Query("ascending", description="Order of sorting: ascending or descending", example="ascending")):
    valid_fields = ["height", "weight", "bmi"]
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Valid fields: height, weight, bmi")
    
    if order not in ["ascending", "descending"]:
        raise HTTPException(status_code=400, detail="Valid options: ascending, descending")
        
    data = data_loader()

    sort_order = True if order == "descending" else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by), reverse=sort_order)
    
    return sorted_data

@app.post("/create")
def create_patient(patient: Patient):
    data = data_loader()

    if patient.id in data:
        raise HTTPException(status_code=400, detail=f"Patient with this ID already exists")
    else:
        data[patient.id] = patient.model_dump(exclude={"id"})
        with open("patients.json", "w") as file:
            json.dump(data, file)
    return {"message": "Patient created successfully"}