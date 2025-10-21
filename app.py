import warnings

from download_utils import DownloadUtils
warnings.filterwarnings("ignore", category=UserWarning)  # ignore warnings from CUDA

import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel

from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry import metrics, trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando aplicación...")
    # Descargar modelos
    DownloadUtils().download_all()
    yield
    print("🛑 Cerrando aplicación...")

# --- FastAPI ---
app = FastAPI(title="API de Ofuscación de Texto", lifespan=lifespan)

# Definir recurso (nombre del servicio)
resource = Resource.create({"service.name": "ofuscar-api"})

# URL del collector (puede venir por variable de entorno)
collector_url = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://chatia-opentelemetry-collector.chatia-desa.svc.cluster.local:4317")

# Exportadores OTLP (métricas y trazas)
metric_exporter = OTLPMetricExporter(endpoint=collector_url, insecure=True)
span_exporter = OTLPSpanExporter(endpoint=collector_url, insecure=True)

# Configurar métricas
metric_reader = PeriodicExportingMetricReader(metric_exporter)
metrics_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(metrics_provider)

# Configurar trazas
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)

# Instrumentar FastAPI y Requests
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Crear un contador de requests
meter = metrics.get_meter(__name__)
request_counter = meter.create_counter(
    name="requests_total",
    description="Número total de requests procesadas",
    unit="1",
)

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
    motor: str = "scrubadub"

class TextoDesofuscarRequest(BaseModel):
    texto_ofuscado: str
    mapeos: dict

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/ofuscar")
def ofuscar(request: TextoRequest):
    """
    Para ofuscar, el cliente debe enviar:\n
        {\n
            "texto": "Mi número de teléfono es (221) 455-5555 y mi correo es pepe@argento.com...",\n
            "motor": "scrubadub"\n
        }\n
    Opciones de motor:\n
    ➡️scrubadub (por defecto)\n
    ➡️presidio\n
    """    

    from presidio_utils import PresidioUtils
    from scrubadub_utils import ScrubadubUtils


    request_counter.add(1, {"endpoint": "/ofuscar"})
    motor = request.motor

    if motor == "scrubadub":
        ofuscador = ScrubadubUtils()
    elif motor == "presidio":
        ofuscador = PresidioUtils()
    else:
        return {"error": "Motor no reconocido. Opciones: scrubadub, presidio"}    
    
    return ofuscador.ofuscar(request.texto)

@app.post("/desofuscar")
def desofuscar(request: TextoDesofuscarRequest):
    """
    Para desofuscar, el cliente debe enviar:
    {
        "texto_ofuscado": "...",
        "mapeos": {...}
    }
    """
    request_counter.add(1, {"endpoint": "/desofuscar"})
    data = request.model_dump()
    text = data.get("texto_ofuscado", "")
    mapeos = data.get("mapeos", {})

    for _, mapping in mapeos.items():
        for original, reemplazo in mapping.items():
            text = text.replace(reemplazo, original)

    return {"texto_desofuscado": text}
