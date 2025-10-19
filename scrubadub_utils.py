import re
import os
import hashlib
import scrubadub
from scrubadub.filth import Filth
from scrubadub.detectors.catalogue import register_detector
from scrubadub.detectors import Detector
import spacy

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

class NameFilth(Filth):
    type = "name"

class DateFilth(Filth):
    type = "date"

class OrgFilth(Filth):
    type = "org"


class ScrubadubUtils:

    def __init__(self):
        pass

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
        regex = re.compile(r'[A-Za-z]{2}-\d{2}-\d{2}-\d{1,6}-\d{2}[-/]\d{2}')

    apertura = os.getenv("TAG_APERTURA", "")
    cierre = os.getenv("TAG_CIERRE", "")

    def ofuscar(self, text: str):
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
            "date": {"output": "fechas", "prefix": "DATE"},
        }

        @register_detector
        class LocalSpacyDetector(Detector):
            name = "local_spacy"
            
            nlp = spacy.load("modelos/en_core_web_trf-3.8.0/en_core_web_trf/en_core_web_trf-3.8.0")

            def iter_filth(self, text, document_name=None):
                doc = self.nlp(text)
                for ent in doc.ents:
                    # print(ent.text, ent.label_)
                    if ent.label_ == "PERSON":
                        yield NameFilth(beg=ent.start_char, end=ent.end_char, text=ent.text)
                    elif ent.label_ == "DATE":
                        yield DateFilth(beg=ent.start_char, end=ent.end_char, text=ent.text)
                    # elif ent.label_ == "ORG":
                    #     yield OrgFilth(beg=ent.start_char, end=ent.end_char, text=ent.text)




        # --- Inicialización ---
        scrubber = scrubadub.Scrubber(locale="es_AR")
        scrubber.add_detector(LocalSpacyDetector())
        scrubber.add_detector(self.CBUDetector)
        scrubber.add_detector(self.CreditCardDetector)
        scrubber.add_detector(self.DNIDetector)
        scrubber.add_detector(self.NOTADetector)
        scrubber.add_detector(self.IPPDetector)


        temp_maps = {
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

                key = config["output"]
                if key not in temp_maps:
                    temp_maps[key] = {}

                text_map = temp_maps[key]
                prefix = config["prefix"]

                if original_text not in text_map:
                    unique_id = hashlib.sha256(original_text.encode('utf-8')).hexdigest()[:8]
                    text_map[original_text] = f"{self.apertura}{prefix}_{unique_id}{self.cierre}"

                text = text.replace(original_text, text_map[original_text])

        # Retornamos el texto ofuscado y los mapeos
        return {
            "texto_ofuscado": text,
            "mapeos": temp_maps,
            "motor": "scrubadub"
        }
