from volair_on_PREM.api.utils.configs import *


from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.name")
resource = Resource.create({"service.name": "API"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)


if infrastackai:
    # Adds span processor with the OTLP exporter to the tracer provider
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint="https://collector-us1-http.infrastack.ai/v1/traces",
                headers=(("infrastack-api-key", infrastackai_api_key),),
            )
        )
    )
