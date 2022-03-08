from typing import Optional
from fastapi import FastAPI
from datetime import datetime
import sys
import os
import script
import base64
import json

    
app = FastAPI()

path = "C:/Users/SalvatoreInvidia/Desktop/fastapi_prova_salva/images/base_images/"



@app.get("/api/test")
async def test(direct):
    # inizializza time
    now = datetime.now()
    start = datetime.timestamp(now)

    # recupera i file
    files = os.listdir("images/base_images/"+direct)

    # verifica che i file non esistano già
    files2 = os.listdir("images/merged_images")
    if(direct.split('/')[0] not in files2):
        os.mkdir("images/merged_images/"+direct)
    else:
        dir = 'images/merged_images/'+direct.split('/')[0]
        for file in os.listdir(dir):
            os.remove("images/merged_images/"+direct+"/"+file)


    ###############################################################
    # esegue la conversione di tutti i file presenti in base_images
    ################################################################
    
    #inizializza array
    converted_images = []
    # esegue le funzioni
    for file in files:
        converted = script.converting(direct, file)
        converted_images.append(converted)
        # inizializza array di risposta



    ###############################################################
    # esegue il marging  di tutte le immagini convertite in jpeg
    ###############################################################

    #inizializza array
    merged_images = []

    # scorri i file nell'array in coppia
    for i in range(len(converted_images)-1):
        if(i % 2 == 0):
            images = [converted_images[i], converted_images[i+1]]
            merged = script.merging(direct, images, i)
            merged_images.append(merged)


    ###############################################################
    # legge il codice a barre o il numero sottostante di ogni immagine
    ###############################################################
    
    text = script.barcode(converted_images, direct)

    # stampa risultati
    print(str(json.dumps(text)))

    # finish datetime
    now = datetime.now()
    finish = datetime.timestamp(now) - start

    # stampa statistiche
    print()
    print()
    print("****************************")
    print("****************************")
    print("immagini elaborate: "+str(len(files)))
    print("tempo impiegato: "+str("{:.2f}".format(finish)) + ' s')
    print("pdf risultanti: "+str("{:.0f}".format(len(files)/2)))
    print("number of code extracted "+str(len(text["buoni"])))
    print("****************************")
    print("****************************")







@app.get("/api/converted")
async def convert(direct):
    files = os.listdir("images/base_images/"+direct)

    converted_images = []
    
    for file in files:
        converted = script.converting(direct, file)
        converted_images.append(converted)
    
    return converted_images

@app.get("/api/merged")
async def merge(direct):

    # inizializza time
    now = datetime.now()
    start = datetime.timestamp(now)

    files = os.listdir("images/base_images/"+direct)

    # verifica che i file non esistano già
    files2 = os.listdir("images/merged_images")
    if(direct.split('/')[0] not in files2):
        os.mkdir("images/merged_images/"+direct)
    else:
        dir = 'images/merged_images/'+direct.split('/')[0]
        for file in os.listdir(dir):
            os.remove("images/merged_images/"+direct+"/"+file)

    #inizializza array
    merged_images = []
    converted_images = []
    
    # esegue le funzioni
    for file in files:
        converted = script.converting(direct, file)
        converted_images.append(converted)

    # scorri i file nell'array in coppia
    for i in range(len(converted_images)-1):
        if(i % 2 == 0):
            images = [converted_images[i], converted_images[i+1]]
            merged = script.merging(direct, images, i)
            merged_images.append(merged)

    # finish datetime
    now = datetime.now()
    finish = datetime.timestamp(now) - start

    # stampa statistiche
    print()
    print()
    print("****************************")
    print("****************************")
    print("immagini elaborate: "+str(len(files)))
    print("tempo impiegato: "+str("{:.2f}".format(finish)) + ' s')
    print("****************************")
    print("****************************")

    return merged_images