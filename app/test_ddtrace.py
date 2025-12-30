from ddtrace import tracer

# Start a manual trace
with tracer.trace("test.trace") as span:
    span.set_tag("test.key", "hello_ddtrace")
    print("Tracing a test span...")

# Print tracer stats (just to see if the trace was recorded)
print("Trace finished. Check Datadog APM after sending this trace.")
