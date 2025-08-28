Commands leraned:

kubectl get pods -n ingress-nginx
kubectl logs <pod-name>
kubectl -n ingress-nginx logs ingress-nginx-controller-<pod-suffix>
kubectl exec -it <pod-name> -- /bin/sh

curl -v http://query-service:8002/query?q=test

kubectl get configmaps
kubectl describe configmap ecommerce-config
kubectl get secrets
kubectl describe secret aws-credentials

kubectl get ingress
kubectl describe ingress ecommerce-ingress
kubectl apply -f ingress.yaml


Issue 2: Missing AWS Credentials

Symptom: Query service returned: Could not load credentials from any providers.

Cause: AWS credentials were missing in Kubernetes deployment.

Solution: Create Kubernetes Secret for AWS credentials.

kubectl create secret generic aws-credentials \
  --from-literal=AWS_ACCESS_KEY_ID=<your-access-key> \
  --from-literal=AWS_SECRET_ACCESS_KEY=<your-secret-key>



Issue 4: Ingress Access

Symptoms:

Using IP in host: field gave error must be a DNS name, not an IP address.

Accessing via ingress gave 404 errors.

Solutions:

Removed host: from ingress.

Exposed ingress controller as NodePort:

kubectl get svc -n ingress-nginx


Updated Ingress for frontend:

spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 8000


Result: Access frontend at http://<ec2-ip>:<nodeport>.



# ADDITIONAL BEST PRACTICES:
# - Horizontal Pod Autoscaling (HPA) for scaling
# - NetworkPolicies to control traffic between microservices
# - Centralized logging & monitoring (Prometheus/Grafana)
# - Resource limits to avoid node starvation
# - Proper readiness & liveness probes
# - Versioned container images for deterministic deployments
# - Rolling Updates
# - Resource Requests and Limits
# - Namespace Management

# - Use separate namespaces for dev, staging, and production to avoid resource conflicts.
