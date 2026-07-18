from fastapi import FastAPI, Path, HTTPException, Query
#Path is used to define and validate path parameters in your api. A path parameter is a value that is a part of your url.
#HTTPException is a class provided by fastapi that lets you stop processing a request AND return an HTTP error response to the client.
#Query is used to recieve, validate and document query parameters from the url. Query Parameters are part of url that comes after '?' .

from fastapi.responses import JSONResponse
#jsonresponse ek response hai ki aapka kaam ho gaya hai so we have to show it, so we use jsonresponse

from pydantic import BaseModel, Field, computed_field
#Basemodel is to define the structure and validation rules.
#Field is used to add additional rules or validation rules, default values, descriptions and metadata to the attributes. eg. if name is a field then no. of characters = 50 is a validation rule
#computed_field is used to calculate dynamic fields that are not given by the user and we have to calculate it 
from typing import Annotated, Literal, Optional
#Annotatd is description add karne ke liye
#Literal is so that ham options dena chahte hai jaise in this case male, female and others
#Optional is a typehint from typing, it tells that a variable or parameter can either have a specific type or 'None' datatype.

import json

#-----------------------------------------------------------------------------------

app = FastAPI() #app naam se hamne ek object banaya hai FastAPI class ka

class Patient(BaseModel): #means hamne ek class banayi jo inherit karegi basemodel class se. Ab hame fields add karni hai jo ek patient ko create karne ki process me required hogi. Patients.json me jo name, age, weight etc. hai, that are the fields that are required 

    id : Annotated[str, Field(..., description='ID of the patient', examples=['P001'])] #3 dots means field required
    name : Annotated[str, Field(..., description='Name of the patient')]
    city : Annotated[str, Field(..., description='City where the patient is living')]
    age : Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient' )]
    gender : Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height : Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight : Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    #All this above code is so that the user could have a good description of all the required fields that are necessary to fill.
    #We have to give some time and patience to this part of our code too

    '''now we are creating a new computed field'''
    @computed_field
    @property
    def bmi(self) -> float: #is computed field ka naam hoga bmi, aur isko self milega, aur jo ye return karega vo ek float datatype hoga, aur next line me ham bmi calc karenge
        bmi = round(self.weight/(self.height**2),2) #isko ham 2 digit tak roundoff karenge
        return bmi
    '''iss poori process me ham dynamically bmi calc kar rahe hai on the go'''
    
    '''verdict wali computed field ke code ko trigger karne k time isme vo self.bmi ko bhi trigger karega to values pehle oopar wale code ko run karke values nikalegi.'''
    @computed_field 
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'

#-----------------------------------------------------------------------

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]
    #So ab kuch aa rha hai ya ni aa raha hai sab kuch ham recieve kar lenge, nothing is required
#------------------------------------------------------------------------

@app.get("/") #yaha decorator ki help se hamne ek route banaya  "/" home route
def hello():
    return {'message': 'Patient management system API'}
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

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)#ham wo data de rahe hai jo hame input mil raha hai aur ham dump kar rahe hai file ke andar
#so it is a function jise ham ek dictionary denge to wo ise json file me daal dega


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

#---------------------------------------------------------------------- 

'''Ab ham hamara endpoint design karenge jo iss above pydantic model ki help se request body se data lega aur hamare patient database me add karega.'''

@app.post('/create')
def create_patient(patient: Patient): #ab hame ek function banana hai create patient karke to yaha par user apne patient ka saara data bhejega uska id, weight, age etc in the form of json aur ham use recieve karenge in a variable called patient aus iss variable ka datatype hai Patient (hamara pydantic model) Hamara pydantic model usme saare rules lagayega aur dekhega ki data sahi format me aaya hai ya nahi. Agar kooi bhi format sahi nahi hua to isi step me error aa jayega.

    #load existing data 
    data = load_data() #dict form me patients ka saara data aa jayega from patients.json   #data here is a python dictionary


    #check if the patient already exist
    if patient.id in data:
        raise HTTPException (status_code=400, detail='Patient already exists')

    #add new patient to the database

    #and we have to add the pydantic object 'patient' in the existing 'data' which is a python dictionary
    #So firstly we have to change the pydatic object 'patient' into a dictionary 
    data[patient.id] = patient.model_dump(exclude=["id"])#converts a pydantic object into a dictionary #means ki ID ko chhod ke name, city, genger, etc, ko ham 'data' ke andar add kar rahe hai by creating a new key i.e 'patient.id'

    #save into the json file

    #for this we have to first create a utility functio just like load data. so we will go up and create the save_data function 

    save_data(data)

    return JSONResponse(status_code=201, content={'message': 'Patient created successfully'})

#----------------------------------------------------------

@app.put('/edit/{patient_id}') #hamare endpoint ka naam hai edit aur ise ek patient_id as path parameter milegi
def update_patient(patient_id:str, patient_update: PatientUpdate):#ek update_patient function bana lenge aur ise 2 cheeze milengi, patient id ise path parameter se milegi, second hame milegi ek request body jisme hamara client patient ka naya information batake bhejega jese ki city aur weight change hua hai. To ye information ham recieve karenge in a variabla called patient_update aur ye ek pydantic object hoga i.e PatientObject ka jo hamne oopar banaya

    data = load_data()

    #firstly we have to check ki jo patient id hame mil rahi hai kya vo hamare database me hai ya nahi

    if patient_id not in data:
        raise HTTPException (status_code=404, detail= 'patient not found')
    
    #If patient inside the database then we will extract the info.

    existing_patient_info = data[patient_id] #hame patient_update se city aur weight ke nayi value leni hai aur use existing_patient_info me add karni hai. #existing wale me saari fields hai 
    #pehle to patient_update ko dict me convert karna padega. 

    updated_patient_info = patient_update.model_dump(exclude_unset=True) #we used the exclude_unset value bcz hame bas data me se city aur weight wali field chahiye but if we dont use this ye poori fields ko add kar dega. #whereas unlike existing, isme sirf 2 fields hai.

    for key, value in updated_patient_info.items():
        existing_patient_info[key]= value #existing dictionary me ja rhe hai aur uske andar same key me naya value update kar de rhe hai
        #ab is existing data me nayi values aa gayi hai and now we have to add this to the patient_id key in the data from the existing_patient_info that was updated just now

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id']= patient_id
    patient_pydantic_object = Patient(**existing_patient_info)
    # -> pydantic object -> dict
    existing_patient_info = patient_pydantic_object.model_dump(exclude='id')

    # fir ham iss dict ke oopar next data[patient_id] wala step chala denge 
    #ham iss existing dict jo updated hai iski help se ek pydantic object banayenge #to isse hoga ki nayi updated values ke saath pydantic object banega (Patient class ka jo ko hamne oopar banaya hai aur usme saari fields firse calculate hokar milegi to hame bmi aur verdict bhi mil jayega for the updated data)

    #now add the above dictionary to data
    data[patient_id] = existing_patient_info 

    #save data 

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})


#making github green 🙃

'''Now we will make the delete endpoint and it will only take user id. and ye patient ka id ham url me as a path parameter provdie karenge. HTTP method that we will use is also DELETE.
The flow is - Patient id le rhe hai , usme data load kar rahe hai, then uske andar se vo key-value pair hata de rahe hai jiski key patient_id hai'''

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str): #ek function bana lenge jisko patient_id as an input milegi and it will be a string datatype.

    #load data
    data = load_data()

    #yaha pe ham check lagayenge ki jo patient id hame mil rahi hai kya vo patient database me exist karti hai ya nahi

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found') #then if this error doesn't raise:
    del data[patient_id] #to fir data se patient id ko delete kar denge

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'patient deleted'})

