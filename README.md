# python-ldap
Implementation of basic LDAP authorization service for use within kubernetes and the nginx-ingress-controller.
(idea based on [another-ldap-auth](https://github.com/dignajar/another-ldap-auth))

## Deployment

```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: ldap-auth-adapter
  namespace: <my-namespace>
type: Opaque
data:
  LDAP_MANAGER_BINDDN: <my-bind-dn>
  LDAP_MANAGER_PASSWORD: <my-manager-pw>
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: ldap-auth-adapter
  namespace: <my-namespace>
data:
  config.yaml: |-
    ldapServers:
    - ldap://<host>:<port>
    - ldaps://<host>:<port>
    my-config-key-1:
    - searchBase: ou=,base-1,c=...,...
      requiredGroup: cn=...,ou=...,...
    - searchBase: ou=,base-2,c=...,...
      requiredGroup: cn=...,ou=...,...
    my-config-key-2:
    - searchBase: ou=,base-1,c=...,...
      requiredGroup: cn=...,ou=...,...
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ldap-auth-adapter
  namespace: <my-namespace>
  labels:
    app: ldap-auth-adapter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ldap-auth-adapter
  template:
    metadata:
      labels:
        app: ldap-auth-adapter
    spec:
      containers:
        - image: trutty/python-ldap:latest
          name: ldap-auth-adapter
          ports:
            - name: http
              containerPort: 9000
          livenessProbe:
            httpGet:
              path: /health
              port: 9000
            initialDelaySeconds: 3
          readinessProbe:
            httpGet:
              path: /health
              port: 9000
            initialDelaySeconds: 3
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "100m"
          volumeMounts:
            - mountPath: /config
              name: ldap-auth-adapter
          envFrom:
            - secretRef:
                name: ldap-auth-adapter
      volumes:
        - name: ldap-auth-adapter
          configMap:
            name: ldap-auth-adapter
---
kind: Service
apiVersion: v1
metadata:
  name: ldap-auth-adapter
  namespace: <my-namespace>
spec:
  type: ClusterIP
  selector:
    app: ldap-auth-adapter
  ports:
    - name: ldap-auth-adapter
      port: 80
      protocol: TCP
      targetPort: 9000
---
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: proxy-ingress
  namespace: <some-namespace>
  annotations:
    nginx.ingress.kubernetes.io/auth-url: http://ldap-auth-adapter.<my-namespace>.svc.cluster.local
    nginx.ingress.kubernetes.io/auth-snippet: |
      proxy_set_header Ldap-Config-Key my-config-key-1;
spec:
  rules:
  - host: <target-host>
    http:
      paths:
      - backend:
          serviceName: <ldap-protected-target-service>
          servicePort: <port>
        path: /
```
