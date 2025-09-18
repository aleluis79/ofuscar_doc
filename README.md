# Ofuscar-Doc

Ofuscar-Doc es una API construida con FastAPI que permite ofuscar y desofuscar información sensible en textos, como nombres, teléfonos, emails, CBUs, URLs, tarjetas de crédito y DNIs. Utiliza la librería [scrubadub](https://github.com/LeapBeyond/scrubadub) y generadores de datos ficticios con [Faker](https://faker.readthedocs.io/).

## ¿Qué hace?

- **Ofusca** información sensible en textos, reemplazándola por datos ficticios y delimitadores configurables.
- **Desofusca** textos previamente ofuscados, restaurando los valores originales a partir de los mapeos generados.

## Endpoints principales

- `POST /ofuscar`: Recibe un texto y devuelve el texto ofuscado junto con los mapeos de los datos reemplazados.
- `POST /desofuscar`: Recibe un texto ofuscado y los mapeos, y devuelve el texto original.

## Ejemplo de uso

### Ofuscar

**Request:**
```json
POST /ofuscar
{
  "texto": "Mi número de teléfono es (221) 455-5555 y mi correo es pepe@argento.com"
}
```

**Response:**
```json
{
  "texto_ofuscado": "Mi número de teléfono es {{...}} y mi correo es {{...}}",
  "mapeos": {
    "nombres": {},
    "telefonos": {"(221) 455-5555": "{{...}}"},
    "emails": {"pepe@argento.com": "{{...}}"},
    ...
  }
}
```

### Desofuscar

**Request:**
```json
POST /desofuscar
{
  "texto_ofuscado": "Mi número de teléfono es {{...}} y mi correo es {{...}}",
  "mapeos": {
    "telefonos": {"(221) 455-5555": "{{...}}"},
    "emails": {"pepe@argento.com": "{{...}}"}
  }
}
```

**Response:**
```json
{
  "texto_desofuscado": "Mi número de teléfono es (221) 455-5555 y mi correo es pepe@argento.com"
}
```

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/aleluis79/ofuscar-doc.git
   cd ofuscar-doc
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

   Asegúrate de tener instalado `spacy` y el modelo de idioma correspondiente:
   ```bash
   pip install spacy
   python -m spacy download en_core_web_sm
   ```

## Ejecución

Lanza el servidor de desarrollo con:

```bash
python -m uvicorn app:app --reload
```

Por defecto, la API estará disponible en [http://localhost:8000](http://localhost:8000).

## Documentación interactiva

Accede a la documentación automática de la API en:

- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)

## Dependencias principales

- fastapi
- uvicorn
- scrubadub
- scrubadub_spacy
- faker
- spacy

## Licencia

MIT
