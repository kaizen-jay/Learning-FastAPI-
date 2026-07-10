from fastapi import FastAPI, Path, HTTPException, Query
#Path is used to define and validate path parameters in your api. A path parameter is a value that is a part of your url.
#HTTPException is a class provided by fastapi that lets you stop processing a request AND return an HTTP error response to the client.
#Query is used to recieve, validate and document query parameters from the url. Query Parameters are part of url that comes after '?' .

from pydantic import BaseModel #To define the structure and validation rules 
from typing import Annotated #Ye description add karne ke liye
import json
app = FastAPI() #app naam se hamne ek object banaya hai FastAPI class ka

class Patient(BaseModel): #means hamne ek class banayi jo inherit karegi basemodel class se. Ab hame fields add karni hai jo ek patient ko create karne ki process me required hogi. Patients.json me jo name, age, weight etc. hai, that are the fields that are required 

    id : str
    name : str
    city : str
    age : int
    gender : str
    height : float
    weight : float 


#------------------------------------------------------------------------

@app.get("/") #yaha decorator ki help se hamne ek route banaya  "/" home route
def hello():
    return {'message': 'hello world'}
#this was the first end point of our api 

@app.get("/about")
def aboutt():
    return {'message': 'This website is created by my first api'}
#this was my second end point of our api

#------------------------------------------------------------------------



def load_data(): #kyuki ye kaam hame baar baar karna padega that's why we are making this load function
    with open('patients.json', 'r') as f: #we are opening this in read mode
         data = json.load(f)
    return data 
#jab bhi ham iss function ko call karenge ye iss data ko load karega 

# Now we will create a new endpoint and we name the route '/view'

@app.get('/view')
def view():
     data = load_data()
     return data 

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str):#ye function ban gaya ab hame iska logic likhna hai
    #load all the patients
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')
 
 #Now we are creating an endpoint to sort patients based on some keypoints

@app.get('/sort')
def sort_patients(sort_by:str = Query(..., description= 'Sort on the basis of height, weight or bmi'),order:str = Query('asc', description= 'Sort in ascending or descending order')):
    #Here sort by is the required parameter thats why i put '...' there, and the 'order' is an optional parameter so we've given the value
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail= f'Invalid field selected from {valid_fields}' )
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail= 'Invalid order. Select between asc and desc')
    
    #now we will load data again
    data = load_data()
    sort_order = True if order=='desc' else False
    #ab hame data ko iss tareeke se dikhana hai ki vo sort ho jaaye
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order ) #reverse true hoga to descending order me sorting hogi and false hoga to ascending order me sorting hogi

    return sorted_data

#----------------------------------------------------------------------------

print("I had to make my github green sorry 😭")


