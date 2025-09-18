# Ofuscación de datos antes de enviar a modelos externos

## Técnicas principales

- **Enmascaramiento**
- **Seudonimización**
- **Hashing selectivo**

| Técnica               | Qué hace                                                                                              | Reversible                                      | Ejemplo                                       | Ventajas                                                                                                        | Desventajas                                                                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Enmascaramiento**   | Oculta parcial o totalmente datos reales reemplazándolos por valores falsos o visibles solo en parte. | ✅ (tienes los datos originales detrás)          | `4111 1111 1111 1234` → `**** **** **** 1234` | - Útil para mostrar datos sin exponerlos.<br>- Fácil de aplicar.<br>- Apto para testing o reportes.             | - No protege realmente la información almacenada.<br>- Se puede inferir parte del dato.                                                               |
| **Seudonimización**   | Sustituye datos identificadores por un seudónimo (clave).                                             | ✅ (si se conserva la tabla de correspondencias) | `Juan Pérez` → `USR-00123`                    | - Cumple GDPR.<br>- Permite análisis y re-identificación controlada.<br>- Reduce riesgos de exposición directa. | - Si se filtra la tabla de correspondencias, se rompe la protección.<br>- Mayor complejidad de gestión.                                               |
| **Hashing selectivo** | Aplica función hash solo a campos sensibles (ej: SHA-256, bcrypt).                                    | ❌ (irreversible, salvo fuerza bruta/débil)      | `DNI: 12345678` → `12ab34cd...`               | - Muy seguro si se usa hash fuerte y salt.<br>- Ideal para autenticar o anonimizar datos sensibles.             | - No se puede recuperar el valor original.<br>- Campos distintos pueden necesitar distintos tratamientos.<br>- Menos flexible que la seudonimización. |

👉 **En pocas palabras:**

- **Enmascaramiento** = para mostrar datos parcialmente sin exponerlos.
- **Seudonimización** = para análisis con posibilidad de re-identificar.
- **Hashing selectivo** = para proteger definitivamente datos críticos.

---

## 1. Enmascaramiento

No hay una librería estándar, suele hacerse con funciones personalizadas o librerías de data masking y data anonymization:

- [faker](https://faker.readthedocs.io/en/master/) → generar datos ficticios (nombres, direcciones, tarjetas).
- [mimesis](https://mimesis.name/) → similar a Faker, soporta múltiples idiomas.
- [scrubadub](https://scrubadub.readthedocs.io/en/stable/) → detectar y enmascarar datos sensibles en texto (emails, nombres, direcciones).

## 2. Seudonimización

Lo más común es usar mapas de IDs o bases intermedias para vincular seudónimos ↔ datos reales.

- [hashids](https://hashids.org/python/) → convierte números (IDs) en códigos cortos, reversibles.
- [pandas](https://pandas.pydata.org/) → útil si trabajás con datasets y necesitás reemplazar columnas enteras con seudónimos.

## 3. Hashing selectivo

Para proteger datos de forma irreversible.

- [hashlib](https://docs.python.org/3/library/hashlib.html) (built-in) → SHA-256, SHA-512, etc.
- [bcrypt](https://pypi.org/project/bcrypt/) → recomendado para contraseñas (lento a propósito).
- [argon2-cffi](https://pypi.org/project/argon2-cffi/) → aún más seguro que bcrypt.

---

## 📌 Resumen de librerías útiles en Python

- **Enmascaramiento** → faker, mimesis, scrubadub.
- **Seudonimización** → hashids, pandas (para reemplazos masivos).
- **Hashing selectivo** → hashlib, bcrypt, argon2-cffi.
