from fastapi import FastAPI
from pydantic import BaseModel
import scrubadub
import scrubadub_spacy
import re
from scrubadub.filth import NameFilth, Filth
from faker import Faker
from fastapi.middleware.cors import CORSMiddleware

# --- Definición de Filths personalizados ---
class CBUFilth(Filth):
    type = "cbu"

class CreditCardFilth(Filth):
    type = "credit_card"

class DNIFilth(Filth):
    type = "dni"

# --- Detectores ---
class CBUDetector(scrubadub.detectors.RegexDetector):
    name = 'cbu_detector'
    filth_cls = CBUFilth
    regex = re.compile(r"\b\d{22}\b")

class CreditCardDetector(scrubadub.detectors.RegexDetector):
    name = 'creditCard_detector'
    filth_cls = CreditCardFilth
    regex = re.compile(r"\b(?:\d[ -]?){13,19}\b")

class DNIDetector(scrubadub.detectors.RegexDetector):
    name = 'dni_detector'
    filth_cls = DNIFilth
    regex = re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}\b")

# --- Inicialización ---
fake = Faker(locale="es_AR")
scrubber = scrubadub.Scrubber(locale="es_AR")
scrubber.add_detector(scrubadub_spacy.detectors.SpacyEntityDetector(locale="en_US"))
scrubber.add_detector(CBUDetector)
scrubber.add_detector(CreditCardDetector)
scrubber.add_detector(DNIDetector)

apertura = "{{"
cierre = "}}"

# --- FastAPI ---
app = FastAPI(title="API de Ofuscación de Texto")

# Agregar middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto según tus necesidades de seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextoRequest(BaseModel):
    texto: str

class TextoDesofuscarRequest(BaseModel):
    texto_ofuscado: str
    mapeos: dict

@app.post("/ofuscar")
def ofuscar(request: TextoRequest):
    """
    Para ofuscar, el cliente debe enviar:
    {
        "texto": "Mi número de teléfono es (221) 455-5555 y mi correo es pepe@argento.com..."
    }
    """
    text = request.texto

    # Diccionarios para mantener consistencia
    name_map, phone_map, email_map = {}, {}, {}
    cbu_map, url_map, credit_card_map, dni_map = {}, {}, {}, {}

    for filth in scrubber.iter_filth(text):
        if filth.type == "name":
            original_name = filth.text
            if original_name not in name_map:
                name_map[original_name] = apertura + fake.first_name() + cierre
            text = text.replace(original_name, name_map[original_name])
        elif filth.type == "phone":
            original_phone = filth.text
            if original_phone not in phone_map:
                phone_map[original_phone] = apertura + fake.phone_number() + cierre
            text = text.replace(original_phone, phone_map[original_phone])
        elif filth.type == "email":
            original_email = filth.text
            if original_email not in email_map:
                email_map[original_email] = apertura + fake.email() + cierre
            text = text.replace(original_email, email_map[original_email])
        elif filth.type == "cbu":
            original_cbu = filth.text
            if original_cbu not in cbu_map:
                cbu_map[original_cbu] = apertura + "".join([str(fake.random_digit()) for _ in range(22)]) + cierre
            text = text.replace(original_cbu, cbu_map[original_cbu])
        elif filth.type == "url":
            original_url = filth.text
            if original_url not in url_map:
                url_map[original_url] = apertura + fake.url() + cierre
            text = text.replace(original_url, url_map[original_url])
        elif filth.type == "credit_card":
            original_credit_card = filth.text
            if original_credit_card not in credit_card_map:
                credit_card_map[original_credit_card] = apertura + fake.credit_card_number() + cierre
            text = text.replace(original_credit_card, credit_card_map[original_credit_card])
        elif filth.type == "dni":
            original_dni = filth.text
            if original_dni not in dni_map:
                dni_map[original_dni] = apertura + "".join([str(fake.random_digit()) for _ in range(8)]) + cierre
            text = text.replace(original_dni, dni_map[original_dni])

    # Retornamos el texto ofuscado y los mapeos
    return {
        "texto_ofuscado": text,
        "mapeos": {
            "nombres": name_map,
            "telefonos": phone_map,
            "emails": email_map,
            "cbus": cbu_map,
            "urls": url_map,
            "credit_cards": credit_card_map,
            "dnis": dni_map
        }
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
