from PIL import Image
from io import BytesIO
import sys
import base64

def getAll():
    return {"image":"getAll!!!"}


print (getAll())

path = "C:/Users/SalvatoreInvidia/Desktop/fastapi_prova_salva/images/base_images/"

# convert images
def converting(direct, file):

    # apri immagine
    im = Image.open("images/base_images/"+direct+file)

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