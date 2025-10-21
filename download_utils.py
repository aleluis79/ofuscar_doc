import os
import spacy
import os
import tarfile
import urllib.request
import sys
import subprocess
import importlib
import site
from spacy.cli.download import download 
from transformers import AutoModelForTokenClassification, AutoTokenizer # type: ignore
from pathlib import Path


class DownloadUtils:
    
    path_destino = "./modelos"
    def __init__(self):
        pass

    def __exists(self, path_dir: str):
        return Path(path_dir).exists()

    def __download(self, model_name: str, save_dir: str):
        if self.__exists(save_dir):
            print(f"✅ El modelo {model_name} ya existe en {save_dir}")
            return
        
        try:
            os.makedirs(save_dir, exist_ok=True)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForTokenClassification.from_pretrained(model_name)
            tokenizer.save_pretrained(save_dir)
            model.save_pretrained(save_dir)
            print(f"✅ Modelo {model_name} se descargo a {save_dir}")
        except Exception as e:
            print(f"❌ Error al descargar el modelo {model_name}: {e}")

    def __download_spacy(self, model_name: str, save_dir: str):
        if self.__exists(save_dir):
            print(f"✅ El modelo {model_name} ya existe en {save_dir}")
            return

        try:    
            download(model_name)
            nlp = spacy.load(model_name)
            os.makedirs(save_dir, exist_ok=True)
            nlp.to_disk(save_dir)
            print(f"✅ Modelo {model_name} se descargo a {save_dir}")
        except Exception as e:
            print(f"❌ Error al descargar el modelo {model_name}: {e}")


    def __download_spacy_model_to_folder(self, model_name: str, target_dir: str = "./modelos"):
        if self.__exists(f"{target_dir}/{model_name}-3.8.0"):
            print(f"✅ El modelo {model_name} ya existe en {target_dir}")
            return

        os.makedirs(target_dir, exist_ok=True)
        url = f"https://github.com/explosion/spacy-models/releases/download/{model_name}-3.8.0/{model_name}-3.8.0.tar.gz"
        tar_path = os.path.join(target_dir, f"{model_name}.tar.gz")

        print(f"📥 Descargando {model_name}...")
        urllib.request.urlretrieve(url, tar_path)

        print(f"📦 Extrayendo a {target_dir}...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=target_dir)

        print("✅ Descarga y extracción completa.")
        return os.path.join(target_dir, model_name)

    def __instalar_modelo_spacy_local(self, nombre_modelo: str, ruta_local: str):
        """
        Instala un modelo local de spaCy solo si no está ya instalado.
        """
        try:
            # Verifica si el modelo ya está disponible
            spacy.util.get_package_path(nombre_modelo)
            print(f"✅ El modelo '{nombre_modelo}' ya está instalado.")
        except (OSError, ImportError):
            ruta = Path(ruta_local).resolve()
            print(f"📦 Instalando modelo spaCy desde: {ruta}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", str(ruta)])
            print(f"✅ Modelo '{nombre_modelo}' instalado correctamente.")


    def download_all(self):
        self.__download_spacy_model_to_folder("es_core_news_lg")
        self.__download_spacy_model_to_folder("en_core_web_trf")
        self.__download("samuelalvarez034/PlanTL-GOB-ES-roberta-base-bne-ner", self.path_destino + "/roberta-base-bne-ner")
        self.__instalar_modelo_spacy_local("en_core_web_trf", "modelos/en_core_web_trf-3.8.0")
        self.__instalar_modelo_spacy_local("es_core_news_lg", "modelos/es_core_news_lg-3.8.0")
      

