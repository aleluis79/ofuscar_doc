from fastapi import FastAPI
from pydantic import BaseModel
import scrubadub
import scrubadub_spacy
import re
import hashlib
from scrubadub.filth import NameFilth, Filth
from faker import Faker

# --- Definición de Filths personalizados ---
class CBUFilth(Filth):
    type = "cbu"

class CreditCardFilth(Filth):
    type = "credit_card"

class DNIFilth(Filth):
    type = "dni"

class NOTAFilth(Filth):
    type = "nota"

class IPPFilth(Filth):
    type = "ipp"

# --- Detectores ---
class CBUDetector(scrubadub.detectors.RegexDetector):
    name = 'cbu_detector'
    filth_cls = CBUFilth
    regex = re.compile(r"\b\d{22}\b")

class CreditCardDetector(scrubadub.detectors.RegexDetector):
    name = 'creditCard_detector'
    filth_cls = CreditCardFilth
    regex = re.compile(r"\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}")

class DNIDetector(scrubadub.detectors.RegexDetector):
    name = 'dni_detector'
    filth_cls = DNIFilth
    regex = re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}\b")

class NOTADetector(scrubadub.detectors.RegexDetector):
    name = 'nota_detector'
    filth_cls = NOTAFilth
    regex = re.compile(r'NOTA-\d{1,6}-\d{1,2}-\d{1,2}')

class IPPDetector(scrubadub.detectors.RegexDetector):
    name = 'ipp_detector'
    filth_cls = IPPFilth
    regex = re.compile(r'[A-Za-z]{2}-\d{2}-\d{2}-\d{6}-\d{2}[-/]\d{2}')

# --- Inicialización ---
fake = Faker(locale="es_AR")
scrubber = scrubadub.Scrubber(locale="es_AR")
scrubber.add_detector(scrubadub_spacy.detectors.SpacyEntityDetector(locale="en_US"))
scrubber.add_detector(CBUDetector)
scrubber.add_detector(CreditCardDetector)
scrubber.add_detector(DNIDetector)
scrubber.add_detector(NOTADetector)
scrubber.add_detector(IPPDetector)

apertura = "{{"
cierre = "}}"

# --- FastAPI ---
app = FastAPI(title="API de Ofuscación de Texto")

# Add Cors
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextoRequest(BaseModel):
    texto: str

class TextoDesofuscarRequest(BaseModel):
    texto_ofuscado: str
    mapeos: dict

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/ofuscar")
def ofuscar(request: TextoRequest):
    """
    Para ofuscar, el cliente debe enviar:
    {
        "texto": "Mi número de teléfono es (221) 455-5555 y mi correo es pepe@argento.com..."
    }
    """
    text = request.texto

    field_config = {
        "name": {"output": "nombres", "prefix": "NAME"},
        "phone": {"output": "telefonos", "prefix": "PHONE"},
        "email": {"output": "emails", "prefix": "MAIL"},
        "cbu": {"output": "cbus", "prefix": "CBU"},
        "url": {"output": "urls", "prefix": "URL"},
        "credit_card": {"output": "tarjetas", "prefix": "CREDID_CARD"},
        "dni": {"output": "dnis", "prefix": "DNI"},
        "ipp": {"output": "ipps", "prefix": "IPP"},
        "nota": {"output": "notas", "prefix": "NOTA"},
    }

    temp_maps = {
        "nombres": {},
        "telefonos": {},
        "emails": {},
        "cbus": {},
        "urls": {},
        "tarjetas": {},
        "dnis": {},
        "ipps": {},
        "notas": {},
    }

    try:
        filths = list(scrubber.iter_filth(text))
    except:
        filths = []
  
    for filth in filths:
        # Procesar solo si el tipo está en la configuración        
        config = field_config.get(filth.type, None)
        if config:
            original_text = filth.text
            text_map = temp_maps[config["output"]]
            prefix = config["prefix"]

            if original_text not in text_map:
                unique_id = hashlib.sha1(original_text.encode()).hexdigest()[:4]
                text_map[original_text] = f"{apertura}{prefix}_{unique_id}{cierre}"

            text = text.replace(original_text, text_map[original_text])

    # Retornamos el texto ofuscado y los mapeos
    return {
        "texto_ofuscado": text,
        "mapeos": temp_maps,
    }

@app.post("/desofuscar")
def desofuscar(request: TextoDesofuscarRequest):
    """
    Para desofuscar, el cliente debe enviar:
    {
        "texto_ofuscado": "...",
        "mapeos": {...}
    }
    """
    data = request.model_dump()
    text = data.get("texto_ofuscado", "")
    mapeos = data.get("mapeos", {})

    for _, mapping in mapeos.items():
        for original, reemplazo in mapping.items():
            text = text.replace(reemplazo, original)

    return {"texto_desofuscado": text}