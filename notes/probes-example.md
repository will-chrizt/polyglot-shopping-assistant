Probes are the key to making your application self-healing and resilient in Kubernetes.

Let's break down each probe in your query.yaml file one by one, using an analogy of a new employee starting their job.

1. Startup Probe (startupProbe)
Analogy: "Are you awake, at your desk, and logged into your computer?"

This probe runs first and only once at the beginning of the container's life. Its sole purpose is to determine if the application has successfully started up. This is especially important for applications like yours that might have a slow start time because they need to connect to other services (like the product-service) or initialize connections (like to AWS Bedrock).

What it's doing exactly:

Mechanism: Every 5 seconds (periodSeconds), Kubernetes sends an HTTP GET request to http://<pod-ip>:8002/query?q=startup.

Patience: It will allow the application to fail this check up to 24 times (failureThreshold). This gives your query-service a generous startup window of 2 minutes (24 tries * 5 seconds = 120 seconds).

Outcome:

If it succeeds once: The startup probe is finished and never runs again. Kubernetes then activates the liveness and readiness probes to begin their regular checks.

If it fails 24 times in a row: Kubernetes concludes the application is broken and cannot start. It will kill the container, and the Deployment will create a new one to try again.

2. Liveness Probe (livenessProbe)
Analogy: "Are you still conscious?"

This probe runs continuously after the startup probe has succeeded. Its purpose is to check if your application is still running or if it has frozen, deadlocked, or entered an unrecoverable state where it's no longer functional.

What it's doing exactly:

Mechanism: Every 15 seconds (periodSeconds), Kubernetes sends an HTTP GET request to http://<pod-ip>:8002/query?q=liveness.

Tolerance: It will only take action if the check fails 3 times in a row (failureThreshold). This prevents a restart due to a single, temporary glitch. If a check fails, it waits another 15 seconds and tries again.

Outcome:

If it succeeds: Kubernetes does nothing. The application is considered "alive" and healthy.

If it fails 3 times in a row: Kubernetes concludes the application is deadlocked and beyond recovery. It kills and restarts the container in an attempt to bring it back to a healthy state. This is the core of Kubernetes' self-healing capability.

3. Readiness Probe (readinessProbe)
Analogy: "Are you ready to take on a new task right now?"

This probe also runs continuously after the startup probe has succeeded. Its purpose is different from the liveness probe. It determines if your application is ready to accept new traffic. An application might be alive (passing the liveness probe) but temporarily too busy to handle new requests, or perhaps it has lost its connection to a critical dependency like AWS Bedrock.

What it's doing exactly:

Mechanism: Every 5 seconds (periodSeconds), Kubernetes sends an HTTP GET request to http://<pod-ip>:8002/query?q=readiness.

Tolerance: It will take action if the check fails 3 times in a row (failureThreshold).

Outcome:

If it succeeds: Kubernetes marks the pod as "Ready". The Kubernetes Service (named query-service) will include this pod in its list of active endpoints and send user traffic to it.

If it fails 3 times in a row: Kubernetes marks the pod as "Not Ready". It removes the pod from the service's endpoints, so no new traffic is sent to it. Crucially, it does not kill the container. This gives the application time to recover (e.g., re-establish a connection to the database). Once the readiness probe starts succeeding again, Kubernetes will automatically add the pod back to the service to receive traffic.

Summary Table
Probe Type	Purpose	Kubernetes Action on Failure
Startup Probe	Has the application started successfully?	Restarts the container if it fails to start within the time limit.
Liveness Probe	Is the application still running or has it frozen?	Restarts the container.
Readiness Probe	Is the application ready to handle new traffic?	Stops sending traffic to the container until it recovers.
