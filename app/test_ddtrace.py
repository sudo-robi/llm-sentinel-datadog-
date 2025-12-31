from ddtrace import tracer

with tracer.trace("test.trace") as span:
    span.set_tag("test.key", "hello_ddtrace")
    print("Tracing a test span...")

print("Trace finished. Check Datadog APM after sending this trace.")
