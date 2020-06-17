import json
import os
import sys
import requests
import time
# If you are using a Jupyter notebook, uncomment the following line.
# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from io import BytesIO

missing_env = False
SUBSCRIPTION_KEY = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
# Variables para traer el endpoint y keys de las variables de entorno
if 'COMPUTER_VISION_ENDPOINT' in os.environ:
    endpoint = os.environ['COMPUTER_VISION_ENDPOINT']
else:
    print("From Azure Cogntivie Service, retrieve your endpoint and subscription key.")
    print("\nSet the COMPUTER_VISION_ENDPOINT environment variable, such as \"https://westus2.api.cognitive.microsoft.com\".\n")
    missing_env = True

if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
    subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
else:
    print("From Azure Cogntivie Service, retrieve your endpoint and subscription key.")
    print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable, such as \"1234567890abcdef1234567890abcdef\".\n")
    missing_env = True

if missing_env:
    print("**Restart your shell or IDE for changes to take effect.**")
    sys.exit()

#Endpoint para reconocimiento de texto
text_recognition_url = endpoint + "/vision/v3.0/read/analyze"

image_url = open('imagen.jpg', 'rb')
headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY}
def reconocer_imagen():
    #Data es la imagen que desea abrir, headers es para saber si va a usar una imagen local o un url de internet
    response = requests.post(
        text_recognition_url, headers=headers, data=image_url)
    response.raise_for_status()

    print("RESPONSE",response)
    return response

def reconocer_texto():
    #Trae a response desde el método anterior
    response = reconocer_imagen()

    # Tiene el uri para trabajar en el reconocimiiento del texto
    operation_url = response.headers["Operation-Location"]

    # Para reconocer el texto abre un hilo, por lo tanto poll es la variable que está a la espera de saber que terminó
    analisis = {}
    poll = True
    while (poll):
        respuesta_final = requests.get(
            operation_url, headers=headers)

        analisis = respuesta_final.json()
        
        print(json.dumps(analisis, indent=4))

        time.sleep(1)
        if ("analyzeResult" in analisis):
            poll = False
        if ("status" in analisis and analisis['status'] == 'failed'):
            poll = False

    poligonos = []
    if ("analyzeResult" in analisis):
        # Extrae el texto y los bordes de a donde está.
        poligonos = [(line["boundingBox"], line["text"])
                    for line in analisis["analyzeResult"]["readResults"][0]["lines"]]


    # Muestra la imagen y el texto la versión computarizada
    image = Image.open("imagen.jpg")
    ax = plt.imshow(image)
    for poligono in poligonos:
        vertices = [(poligono[0][i], poligono[0][i+1])
                    for i in range(0, len(poligono[0]), 2)]
        text = poligono[1]
        patch = poligono(vertices, closed=True, fill=False, linewidth=2, color='y')
        ax.axes.add_patch(patch)
        plt.text(vertices[0][0], vertices[0][1], text, fontsize=20, va="top")
    plt.show()

reconocer_texto()