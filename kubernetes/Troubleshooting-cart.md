# =================================================================
# Troubleshooting Summary
# =================================================================
# This document details the steps taken to get the cart-service running in Kubernetes.
#
# 1. Error: Pod stuck in `Pending` state.
#    - Reason: The event logs showed "unbound immediate PersistentVolumeClaims".
#      The PersistentVolumeClaim (PVC) requested storage, but no PersistentVolume (PV)
#      was available in the cluster to fulfill the request.
#    - Solution: A PersistentVolume was created in the cluster, allowing the PVC to bind.
#
# 2. Error: Pod in `CrashLoopBackOff` state.
#    - Reason: The pod logs showed a `java.sql.SQLException: Permission denied` error when
#      trying to create the `cart.db` file. The container, running as a non-root user,
#      lacked permissions to write to the mounted volume.
#    - Solution: A `securityContext` was added to the pod spec to run the container with
#      user ID 1000 and group ID 1000.
#
# 3. Error: Pod in `CrashLoopBackOff` state again.
#    - Reason: The pod logs showed "Error: Unable to access jarfile app.jar".
#      Mounting the volume at `/app` hid the application JAR file that was in the base image.
#    - Solution: The volume `mountPath` was changed to a dedicated `/app/data` directory,
#      and the `SPRING_DATASOURCE_URL` environment variable was set to point to the new path.
#
# 4. Error: The `initContainer` (added to fix permissions) was in `CrashLoopBackOff`.
#    - Reason: The `initContainer` needed to run the `chown` command, which requires root
#      privileges. However, the pod-level `securityContext` forced it to run as a non-root user.
#    - Solution: A specific `securityContext` with `runAsUser: 0` (root) was added
#      directly to the `initContainer` definition, overriding the pod-level setting.
#      This allowed it to fix permissions before the main, non-root application container started.
# =================================================================

# =================================================================
# 1. PersistentVolumeClaim (PVC) for Database Storage
# =================================================================
# This object requests a piece of storage from the cluster to persist
# the SQLite database file. It's the K8s equivalent of a Docker named volume.
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cart-db-pvc # The name we'll use to refer to this storage claim.
spec:
  accessModes:
    - ReadWriteOnce # This volume can be mounted as read-write by a single node.
  resources:
    requests:
      storage: 1Gi # Request 1 Gibibyte of storage.

---
# =================================================================
# 2. Deployment for the Cart Service
# =================================================================
# This object manages the lifecycle of the cart-service pod, ensuring
# it's always running and configured correctly.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cart-service-deployment
  labels:
    app: cart-service
spec:
  replicas: 1 # Run a single instance, as it's a stateful service.
  selector:
    matchLabels:
      app: cart-service
  template:
    metadata:
      labels:
        app: cart-service # The label the Service will use to find this pod.
    spec:
      securityContext:
        runAsUser: 1000
        fsGroup: 1000
      # --- FIX: ADD INIT CONTAINER TO SET PERMISSIONS ---
      # This container runs before the main app container to fix volume permissions.
      initContainers:
      - name: init-permissions
        image: busybox:1.32
        # --- FIX: RUN INIT CONTAINER AS ROOT ---
        # This container needs root privileges to run 'chown'.
        # The pod-level securityContext will still apply to the main container.
        securityContext:
          runAsUser: 0
        command: ['sh', '-c', 'chown -R 1000:1000 /app/data']
        volumeMounts:
        - name: cart-storage
          mountPath: /app/data
      containers:
        - name: cart-service
          image: willchrist/cart:v2 # The Docker image to run.
          ports:
            - containerPort: 8080 # The port the application listens on inside the container.
          env:
            - name: SPRING_DATASOURCE_URL
              value: "jdbc:sqlite:/app/data/cart.db"
          volumeMounts:
            - name: cart-storage # The name of the volume to mount.
              mountPath: /app/data # Mount the storage inside the app's working directory.
      volumes:
        - name: cart-storage
          persistentVolumeClaim:
            claimName: cart-db-pvc # Use the PersistentVolumeClaim created above.

---
# =================================================================
# 3. Service to Expose the Deployment
# =================================================================
# This object provides a stable DNS name and IP address for other services
# inside the cluster to connect to the cart-service.
apiVersion: v1
kind: Service
metadata:
  name: cart-service # This name becomes the DNS name for other services to use.
spec:
  type: ClusterIP # Exposes the service only within the cluster.
  selector:
    app: cart-service # Forwards traffic to any pod with this label.
  ports:
    - protocol: TCP
      port: 8080 # The port that other services will connect to.
      targetPort: 8080 # The port on the pod to forward traffic to. yo
