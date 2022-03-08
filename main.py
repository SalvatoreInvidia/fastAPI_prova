from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
import script

    
app = FastAPI()

path = "C:/Users/SalvatoreInvidia/Desktop/fastapi_prova_salva/images/base_images/"

@app.get("/api")
async def convert(direct):
    files = os.listdir("images/base_images/"+direct)

    converted_images = []
    
    for file in files:
        converted = script.converting(direct, file)
        converted_images.append(converted)
    
    return converted_images