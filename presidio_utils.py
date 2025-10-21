import csv
import hashlib
import os
import re
import unicodedata
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_analyzer.nlp_engine import TransformersNlpEngine
from presidio_analyzer.nlp_engine import TransformersNlpEngine, NerModelConfiguration

class AccentInsensitiveNameRecognizer(PatternRecognizer):
    supported_entity: str
    supported_language: str

    def quitar_acentos_simple(self, s: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    def __init__(self, deny_list, supported_entity="CUSTOM_NAME", supported_language="es"):
        super().__init__(supported_entity=supported_entity, supported_language=supported_language, deny_list=deny_list)
        self.supported_entity = supported_entity
        self.supported_language = supported_language
        # Preprocesamos deny_list para normalizar y preparar el patrón regex
        nombres_normalizados = [re.escape(self.quitar_acentos_simple(n.lower())) for n in deny_list]
        # Construimos un solo patrón regex que busque coincidencias por palabra completa
        self.regex = re.compile(r"\b(" + "|".join(nombres_normalizados) + r")\b", re.UNICODE)

    def analyze(self, text, entities, nlp_artifacts=None, regex_flags=None):
        text_lower = text.lower()

        # Creamos texto normalizado (sin acentos)
        normalized_chars = []
        orig_index_map = []
        for i, ch in enumerate(text_lower):
            norm = ''.join(
                c for c in unicodedata.normalize('NFD', ch)
                if unicodedata.category(c) != 'Mn'
            )
            for c in norm:
                normalized_chars.append(c)
                orig_index_map.append(i)

        normalized_text = ''.join(normalized_chars)

        results = []
        for match in self.regex.finditer(normalized_text):
            start_norm, end_norm = match.span()
            start_orig = orig_index_map[start_norm]
            end_orig = orig_index_map[end_norm - 1] + 1
            results.append(
                RecognizerResult(
                    entity_type=self.supported_entity,
                    start=start_orig,
                    end=end_orig,
                    score=1.0
                )
            )
        return results


class PresidioUtils:

    apertura = os.getenv("TAG_APERTURA", "")
    cierre = os.getenv("TAG_CIERRE", "")
    path_diccionarios = os.getenv("PATH_DICCIONARIOS", "diccionarios")

    # Configuración del modelo en español
    model_config = [{
        "lang_code": "es",
        "model_name": {
            #"spacy": "modelos/es_core_news_lg-3.8.0/es_core_news_lg/es_core_news_lg-3.8.0",
            "spacy": "es_core_news_lg",            
            "transformers": "modelos/roberta-base-bne-ner"
    }
    }]




    def __init__(self):
        pass

    def hash_text(self, cadena: str)-> str:
        return hashlib.sha256(cadena.encode('utf-8')).hexdigest()[:8]

    def ofuscar(self, text: str):

        mapping = {}

        ner_model_configuration = NerModelConfiguration(aggregation_strategy="simple", stride=14)
        nlp_engine = TransformersNlpEngine(models=self.model_config, ner_model_configuration=ner_model_configuration)
        analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en", "es"])

        # --- Reconocedor de teléfonos ---
        pattern_phone = Pattern(
            name="es_phone",
            regex=r"\(?\d{2,4}\)?[\s\-]\d{3,4}[\s\-]?\d{3,4}",
            score=0.8
        )
        phone_recognizer = PatternRecognizer(
            supported_entity="PHONE",
            patterns=[pattern_phone],
            supported_language="es"
        )
        analyzer.registry.add_recognizer(phone_recognizer)

        # --- Reconocedor de emails ---
        pattern_email = Pattern(
            name="es_email",
            regex=r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            score=0.9
        )
        email_recognizer = PatternRecognizer(
            supported_entity="EMAIL",
            patterns=[pattern_email],
            supported_language="es"
        )
        analyzer.registry.add_recognizer(email_recognizer)

        # --- Reconocedor de dni ---
        pattern_dni = Pattern(
            name="es_dnu",
            regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}\b",
            score=0.9
        )
        dni_recognizer = PatternRecognizer(
            supported_entity="DNI",
            patterns=[pattern_dni],
            supported_language="es"
        )
        analyzer.registry.add_recognizer(dni_recognizer)

        # --- Reconocedor de nota ---
        pattern_nota = Pattern(
            name="es_nota",
            regex=r'NOTA-\d{1,6}-\d{1,2}-\d{1,2}',
            score=0.9
        )
        nota_recognizer = PatternRecognizer(
            supported_entity="NOTA",
            patterns=[pattern_nota],
            supported_language="es"
        )
        analyzer.registry.add_recognizer(nota_recognizer)

        # --- Reconocedor de IPP ---
        pattern_ipp = Pattern(
            name="es_ipp",
            regex=r'[A-Za-z]{2}-\d{2}-\d{2}-\d{1,6}-\d{2}[-/]\d{2}',
            score=0.9
        )
        ipp_recognizer = PatternRecognizer(
            supported_entity="IPP",
            patterns=[pattern_ipp],
            supported_language="es"
        )
        analyzer.registry.add_recognizer(ipp_recognizer)

        # Crear directorio diccionarios si no existe
        os.makedirs(self.path_diccionarios, exist_ok=True)            

        # Verifico si existe el archivo nombres.csv en el directorio diccionarios
        if not os.path.exists(f"{self.path_diccionarios}/nombres.csv"):
            with open(f"{self.path_diccionarios}/nombres.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                nombres_example = [ 'Amarillo', 'Irma', 'Pablo','Walter','Juan', 'María', 'Carlos', 'Ana', 'José', 'Laura', 'Pedro', 
                            'Miguel', 'Carmen', 'Antonio', 'Isabel', 'Francisco', 'Patricia', 'Manuel', 'Rosa','Sofía', 
                            'Jorge', 'Marta', 'Roberto', 'Lucia', 'Diego', 'Paula', 'Fernando', 'Andrea','Luis', 'Elena',
                            'Raúl', 'Gabriela', 'Alberto', 'Silvia', 'Ricardo', 'Cristina', 'Eduardo', 'Beatriz', 'María'
                            'Sergio', 'Mónica', 'Daniel', 'Claudia', 'Martín', 'Sandra', 'Alejandro', 'Teresa', 'Javier',
                            'Natalia', 'Guillermo', 'Victoria', 'Manuel', 'Paula', 'Fernando', 'Andrea', 'Raúl', 'Gabriela',
                            'Alberto', 'Silvia', 'Ricardo', 'Cristina', 'Eduardo', 'Beatriz', 'Sergio', 'Mónica', 'Daniel',
                            'Claudia', 'Martín', 'Sandra', 'Alejandro', 'Teresa', 'Javier', 'Natalia', 'Guillermo', 'Victoria',
                            'Garcia', 'García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez',
                            'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz', 'Hernández', 'Díaz', 'Moreno',
                            'Álvarez', 'Muñoz', 'Romero', 'Alonso', 'Gutiérrez', 'Navarro', 'Torres',
                            'Domínguez', 'Vázquez', 'Ramos', 'Gil', 'Ramírez', 'Serrano', 'Blanco', 'Molina'
                        ]                
                for nombre in nombres_example:
                    writer.writerow([nombre]) 

        with open(f"{self.path_diccionarios}/nombres.csv", "r", encoding="utf-8") as f:
            nombres = [row[0] for row in csv.reader(f)]

        nombres_recognizer = AccentInsensitiveNameRecognizer(
            supported_entity="CUSTOM_NAME", 
            deny_list=nombres,
            supported_language="es"
        )
        analyzer.registry.add_recognizer(nombres_recognizer)

        entity_map = {
            "PERSON": "nombres",
            "URL": "urls",
            "EMAIL": "emails",
            "DNI": "dnis",
            "NOTA": "notas",
            "IPP": "ipps",
            "PHONE_NUMBER": "telefonos",
            "PHONE": "telefonos",
            "DATE_TIME": "fechas",
            "CUSTOM_NAME" : "nombres"
        }        

        # --- Análisis del texto ---
        results = analyzer.analyze(
            text=text,
            entities=["PERSON", "CUSTOM_NAME", "DATE_TIME", "URL", "PHONE_NUMBER", "PHONE", "EMAIL", "DNI", "NOTA", "IPP"],
            language='es'
        )
        # Construcción del mapa de reemplazo
        for result in results:
            fragment: str = text[result.start:result.end]
            #print("result:", result , "valor:", fragment)
            if (result.score <= 0.5):
                continue
            entity_key = entity_map.get(result.entity_type)
            if not entity_key:
                continue

            if entity_key not in mapping:
                mapping[entity_key] = {}

            hashed = f"{self.apertura}{result.entity_type}_{self.hash_text(fragment)}{self.cierre}"
            mapping[entity_key][fragment] = hashed

        # Reemplazo en el texto original
        new_text = text
        for entity_key, texts in mapping.items():
            for original_text in sorted(texts.keys(), key=len, reverse=True):
                new_text = new_text.replace(original_text, texts[original_text])


        # Retornamos el texto ofuscado y los mapeos
        return {
            "texto_ofuscado": new_text,
            "mapeos": mapping,
            "motor": "presidio"
        }
