import scrubadub
import scrubadub_spacy
import re
import hashlib
from scrubadub.filth import Filth
from faker import Faker

class CBUFilth(Filth):
    type = "cbu"

class CreditCardFilth(Filth):
    type = "credit_card"

class DNIFilth(Filth):
    type = "dni"

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


fake = Faker(locale="es_AR")
scrubber = scrubadub.Scrubber(locale="es_AR")
scrubber.add_detector(scrubadub_spacy.detectors.SpacyEntityDetector(locale="en_US"))
scrubber.add_detector(CBUDetector)
scrubber.add_detector(CreditCardDetector)
scrubber.add_detector(DNIDetector)

# Diccionario para mantener nombres ya reemplazados
name_map = {}
phone_map = {}
email_map = {}
cbu_map = {}
url_map = {}
credit_card_map = {}
dni_map = {}

apertura = "{{"
cierre = "}}"

text_original = """Mi número de teléfono es (221) 455-5555 y mi correo es pepe@argento.com. 
El cliente Juan Bautista Clavero tiene CBU 2850590940090418135201
Mi página web es https://www.argento.com y mi tarjeta de crédito es 1234 5678 9012 3456.
El director es Julio Altamira Fernadez es abogado y su DNI es 12.345.678.
Saludos, Juan Bautista Clavero.
Te: (221) 455-5555
Email: pepe@argento.com
"""

text = text_original

# Iterar sobre los Filth encontrados
for filth in scrubber.iter_filth(text):
    #print(f"{filth.type}: {filth.text}")
    if filth.type == "name":
        original_name = filth.text
        # Si no está en el diccionario, generar uno nuevo
        if original_name not in name_map:
            unique_id = hashlib.sha1(original_name.encode()).hexdigest()[:4]
            name_map[original_name] = apertura + f"NAME_{unique_id}" + cierre
        # Reemplazar en el texto
        text = text.replace(original_name, name_map[original_name])
    elif filth.type == "phone":
        original_phone = filth.text
        # Si no está en el diccionario, generar uno nuevo
        if original_phone not in phone_map:
            unique_id = hashlib.sha1(original_phone.encode()).hexdigest()[:4]
            phone_map[original_phone] = apertura + f"PHONE_{unique_id}" + cierre
        # Reemplazar en el texto
        text = text.replace(original_phone, phone_map[original_phone])
    elif filth.type == "email":
        original_email = filth.text
        # Si no está en el diccionario, generar uno nuevo
        if original_email not in email_map:
            unique_id = hashlib.sha1(original_email.encode()).hexdigest()[:4]
            email_map[original_email] = apertura + f"MAIL_{unique_id}" + cierre
        # Reemplazar en el texto
        text = text.replace(original_email, email_map[original_email])
    elif filth.type == "cbu":
        original_cbu = filth.text
        # Si no está en el diccionario, generar uno nuevo
        if original_cbu not in cbu_map:
            unique_id = hashlib.sha1(original_cbu.encode()).hexdigest()[:4]
            cbu_map[original_cbu] = apertura + f"CBU_{unique_id}" + cierre
        # Reemplazar en el texto
        text = text.replace(original_cbu, cbu_map[original_cbu])
    elif filth.type == "url":
        original_url = filth.text
        # Si no está en el diccionario, generar uno nuevo
        if original_url not in url_map:
            unique_id = hashlib.sha1(original_url.encode()).hexdigest()[:4]
            url_map[original_url] = apertura + f"URL_{unique_id}" + cierre
        # Reemplazar en el texto
        text = text.replace(original_url, url_map[original_url])
    elif filth.type == "credit_card":
        original_credit_card = filth.text
        # Si no está en el diccionario, generar uno nuevo
        if original_credit_card not in credit_card_map:
            unique_id = hashlib.sha1(original_credit_card.encode()).hexdigest()[:4]
            credit_card_map[original_credit_card] = apertura + f"CREDID_CARD_{unique_id}" + cierre
        # Reemplazar en el texto
        text = text.replace(original_credit_card, credit_card_map[original_credit_card])
    elif filth.type == "dni":
        original_dni = filth.text
        # Si no está en el diccionario, generar uno nuevo
        if original_dni not in dni_map:
            unique_id = hashlib.sha1(original_dni.encode()).hexdigest()[:4]
            dni_map[original_dni] = apertura + f"DNI_{unique_id}" + cierre
        # Reemplazar en el texto
        text = text.replace(original_dni, dni_map[original_dni])


print("Texto original:")
print(text_original)

print("Texto ofuscado:")
print(text)

print("Mapeos realizados:")
print("Nombres:", name_map)
print("Teléfonos:", phone_map)
print("Emails:", email_map)
print("CBUs:", cbu_map)
print("URLs:", url_map)
print("Tarjetas de crédito:", credit_card_map)
print("DNIs:", dni_map)

texto_desofuscado = text
for original, reemplazo in name_map.items():
    texto_desofuscado = texto_desofuscado.replace(reemplazo, original)
for original, reemplazo in phone_map.items():
    texto_desofuscado = texto_desofuscado.replace(reemplazo, original)
for original, reemplazo in email_map.items():
    texto_desofuscado = texto_desofuscado.replace(reemplazo, original)
for original, reemplazo in cbu_map.items():
    texto_desofuscado = texto_desofuscado.replace(reemplazo, original)
for original, reemplazo in url_map.items():
    texto_desofuscado = texto_desofuscado.replace(reemplazo, original)
for original, reemplazo in credit_card_map.items():
    texto_desofuscado = texto_desofuscado.replace(reemplazo, original)
for original, reemplazo in dni_map.items():
    texto_desofuscado = texto_desofuscado.replace(reemplazo, original)
print("\nTexto desofuscado:")
print(texto_desofuscado)


if text_original == texto_desofuscado:
    print("El texto desofuscado coincide con el original.")
else:
    print("El texto desofuscado NO coincide con el original.")