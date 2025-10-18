import hashlib
import os
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import TransformersNlpEngine
from presidio_analyzer.nlp_engine import TransformersNlpEngine, NerModelConfiguration

class PresidioUtils:

    apertura = os.getenv("TAG_APERTURA", "")
    cierre = os.getenv("TAG_CIERRE", "")

    # Configuración del modelo en español
    model_config = [{
        "lang_code": "es",
        "model_name": {
            "spacy": "es_core_news_lg",
            "transformers": "samuelalvarez034/PlanTL-GOB-ES-roberta-base-bne-ner"
        }
    }]

    ner_model_configuration = NerModelConfiguration(aggregation_strategy="simple", stride=14)
    nlp_engine = TransformersNlpEngine(models=model_config, ner_model_configuration=ner_model_configuration)
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

    nombres = [ 'Amarillo', 'Irma', 'Pablo','Walter','Juan', 'María', 'Carlos', 'Ana', 'José', 'Laura', 'Pedro', 
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

    nombres_recognizer = PatternRecognizer(
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
        "NOMBRES": "nombres",
        "CUSTOM_NAME" : "nombres"
    }


    def __init__(self):
        pass

    def hash_text(self, cadena: str)-> str:
        return hashlib.sha256(cadena.encode('utf-8')).hexdigest()[:8]

    def ofuscar(self, text: str):

        mapping = {}

        # --- Análisis del texto ---
        results = self.analyzer.analyze(
            text=text,
            entities=["PERSON", "CUSTOM_NAME", "URL", "PHONE_NUMBER", "PHONE", "EMAIL", "DNI", "NOTA", "IPP"],
            language='es'
        )
        # Construcción del mapa de reemplazo
        for result in results:
            fragment: str = text[result.start:result.end]
            #print("result:", result , "valor:", fragment)
            if (result.score <= 0.5):
                continue
            entity_key = self.entity_map.get(result.entity_type)
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
