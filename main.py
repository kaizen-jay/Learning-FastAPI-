from fastapi import FastAPI, Path, HTTPException
import json
app = FastAPI() #app naam se hamne ek object banaya hai FastAPI class ka

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
 


