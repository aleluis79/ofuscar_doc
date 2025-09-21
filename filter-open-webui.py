"""
title: Ofuscador Filter
author: Alejandro
version: 0.1
"""

from pydantic import BaseModel
from typing import Optional
import requests


class Filter:

    class Valves(BaseModel):
        pass

    class UserValves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()
        self.mapeos = {}

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:

        try:
            print("Ingreso a ofuscar ---->")
            # Tomamos el último mensaje del usuario
            last_message = body["messages"][-1]["content"]

            resp = requests.post(
                "http://myapp:8000/ofuscar",
                json={"texto": last_message},
                timeout=5,
            )

            if resp.ok:
                data = resp.json()
                respuesta = data.get("texto_ofuscado")
                self.mapeos = data.get("mapeos")

                prompt = f"""
                Eres un asistente de redacción. 
                Tu tarea es reformular, corregir o mejorar textos, 
                PERO debes preservar intactos todos los fragmentos que aparezcan entre llaves dobles {{ ... }}. 
                
                - Nunca elimines, modifiques ni alteres lo que está dentro de {{ ... }}.  
                - Debes mantener exactamente la misma ortografía, espacios y símbolos entre las llaves. 
                - Puedes cambiar el resto del texto normalmente. 
                - Si necesitas mover las frases, hazlo, pero siempre copiando los fragmentos {{ ... }} tal cual están escritos.

                {respuesta}
                """

                body["messages"][-1]["content"] = prompt
            print(f"Respuesta -> {respuesta}")
            print("Salgo de ofuscar ---->")
            return body

        except Exception as e:
            print(f"[OfuscadorPipe] Error: {e}")
            return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        try:
            print("Ingreso a desofuscar ---->")
            print(f"MAPEOS: {self.mapeos}")
            last_message = body["messages"][-1]["content"]

            resp = requests.post(
                "http://myapp:8000/desofuscar",
                json={"texto_ofuscado": last_message, "mapeos": self.mapeos},
                timeout=5,
            )

            if resp.ok:
                data = resp.json()
                print(f"RESPUESTA JSON= {data}")
                respuesta = data.get("texto_desofuscado")
                body["messages"][-1]["content"] = respuesta
            print(f"Respuesta -> {respuesta}")
            print("Salgo de desofuscar ---->")
            return body
        except Exception as e:
            print(f"[OfuscadorPipe] Error: {e}")
            return body
