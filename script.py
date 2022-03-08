import os
from queue import Empty
import re
import sys
from datetime import datetime
import base64
from io import BytesIO
import json
# immages
from PIL import Image
import cv2
import numpy as np
# OCR
import pytesseract
from pytesseract import Output

from pyzbar.pyzbar import decode


# convert images
def converting(direct, file):

    # apri immagine
    im = Image.open("images/base_images/"+direct+"/"+file)

    # inizializza buffer di memoria
    buffered = BytesIO()

    # conversione
    # se sys.argv[3] => rotate == true allora effettua una rotazione di 180° sull'asse perpendicolare all'immagine
    # if(sys.argv[1] == 'true'):
    #     im.convert("RGB").rotate(180).save(buffered, "JPEG", quality=50)
    # else:
    #     
    im.convert("RGB").save(buffered, "JPEG", quality=50)

    img_str = base64.b64encode(buffered.getvalue())

    # append l'immagine processata all'array di risposta
    converted_images = img_str

    print(converted_images)

    return converted_images


# Merging images
def merging(direct, files, i):

    # formato a4 150dpi
    a4_width = 1240
    a4_height = 1754

    # crea nuova immagine a sfondo bianco
    new_image = Image.new(
        'RGB', (a4_width, a4_height), "WHITE")

    # apri la coppia di immagini
    image1 = Image.open(BytesIO(base64.b64decode(files[0])))
    image2 = Image.open(BytesIO(base64.b64decode(files[1])))

    # inverte la direzione delle immagini
    # if(sys.argv[2] == 'false'):
    #     image2 = Image.open(BytesIO(base64.b64decode(files[0])))
    #     image1 = Image.open(BytesIO(base64.b64decode(files[1])))

    # dimensioni e posizioni della coppia immagini nella nuova immagine creata
    width, height = image1.size
    rapport = int(width)/a4_width
    width = int(width)/rapport
    height = int(height)/rapport
    y0 = (a4_height-(height*2))/2
    y1 = y0 + height

    # ridimensiona le immagini
    image1 = image1.resize((int(width), int(height)))
    image2 = image2.resize((int(width), int(height)))

    # incolla coppia di immagini
    new_image.paste(image1, (0, int(y0)))
    new_image.paste(image2, (0, int(y1)))

    buffered = BytesIO()

    # salva il base64 dell'immagine
    new_image.convert("RGB").save(buffered, "JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    # salva il documento pdf nella cartella
    new_image.convert("RGB").save(
        "images/merged_images/"+direct+"mergedimage_"+str("{:.0f}".format((i/2)+1))+".pdf", "PDF")

    # append l'immagine creata' all'array di risposta

    merged_images = img_str
    return merged_images

# legge il numero sotto il barcode
def numbercode(im22):  # un'immagine

    # L'immagine viene letta e processata in modo tale
    # da recuperare il numero che si trova sotto il codice a barre

    # ritaglia immagine
    image = cropImage(im22, 800, 1900, 2250-1900, 1700-800)
    text_images = []

    # legge l'immagine con TesseractOCR
    custom_config = r'-c tessedit_char_whitelist=0123456789- --psm 6'
    d = pytesseract.image_to_data(
        image, config=custom_config, output_type=Output.DICT)

    # inizializza il formato regolare previsto
    regex = r"^68\d{9}-\d{1}$"
    prog = re.compile(regex)

    for element in d['text']:

        # verifica che il testo trovato rispetti il formato
        result = prog.match(str(element))

        # restituisce il testo se ha avuto qualche riscontro
        if(str(result) != 'None'):
            text_images.append(str(result.group()))

    # verifica che esista almeno un'elemento
    if(len(text_images) >= 1):
        text_images = str("".join(text_images))

    return text_images


# OCR using PyTesseract
def barcode(images, dir):  # array di immagini

    # inizializza array di risposta
    messages = []
    buoni = []
    error = []
    files = os.listdir("images/base_images/"+dir)

    # scorre le immagini
    for i, image in enumerate(images):

        # inizializza l'array di risposta della singola immagine
        text_images = []

        # recupera l'immagine dal base64
        im22 = readCV2(image)

        # verifica che venga letta solo l'immagine frontale
        # if(i % 2 == 0 and sys.argv[3] == "true"):
        if(i % 2 == 0):

            # ritaglia l'immagine introno al barcode
            im3 = cropImage(im22, 800, 1500, 2020-1500, 1700-800)

            # decodifica il barcode
            detectedBarcodes = decode(im3)

            # verifica che sia stato rilevato qualche barcode
            if(len(detectedBarcodes) == 0):

                # altrimenti legge il numero
                number = numbercode(im22)

                # verifica il risultato della lettura del numero
                if (number):

                    # inserisce il numero letto come risultato positivo
                    test = str(number).split("-")
                    number = "".join([test[0], test[1]])
                    buoni.append([files[i], number])
                else:

                    # inserisce un errore riferito al file in cui non rileva nulla
                    error.append("error in file: " + str(files[i]))
            else:
                # legge i singoli barcode rilevati
                for barcode in detectedBarcodes:

                    # verifica il formato del barcode letto
                    # se il formato non è rispettato legge il numero
                    if(len(list(barcode.data)) < 12):
                        number = numbercode(im22)
                        test = str(number).split("-")
                        text_images = "".join([test[0], test[1]])
                    else:
                        # altrimenti restituisce il testo estratto dal barcode
                        text = str(barcode.data).split("'")
                        text_images = str(text[1])
                        text_images = text_images

                    buoni.append([files[i], text_images])

    messages = {'buoni': buoni, 'errors': error}
    return messages


# ritaglia immagine
def cropImage(image, x, y, h, w):

    # L'immagine viene ritagliata secondo le dimensioni inserite,
    # x => x0,
    # y=> y0,
    # h=> y1-y0,
    # w=> x1-x0

    y1 = y+h
    x1 = x+w

    cropped_image = image[y:y1, x:x1]

    return cropped_image


# recupera l'immagine dal base64
def readCV2(image):
    img = base64.b64decode(image)
    npimg = np.fromstring(img, dtype=np.uint8)
    im2 = cv2.imdecode(npimg, 1)
    return im2


# processa l'immagine con opencv
def processaImmagine(image):

    # l'immagine viene processata e normalizzata
    # applicando dei filtri
    # per ottenere risultati più efficienti

    gray = get_grayscale(image)
    rem = remove_noise(gray)
    thresh = thresholding(rem)

    return thresh


# grey scale effect
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 5)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

