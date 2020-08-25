# python-ldap
Implementation of basic LDAP authorization service for use within kubernetes and the nginx-ingress-controller.
(idea based on [another-ldap-auth](https://github.com/dignajar/another-ldap-auth))

## Deployment

````
apiVersion: v1
kind: Secret
metadata:
  name: ldap-auth-adapter
  namespace: ingress-nginx
type: Opaque
data:
  LDAP_MANAGER_BINDDN: <secret-bind-dn>
  LDAP_MANAGER_PASSWORD: <secret-bind-password>
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: ldap-auth-adapter
  namespace: ingress-nginx
data:
  config.yaml: |-
    ldapServers:
    - ldap://<host>:<port>
    - ldaps://<host>:<port>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ldap-auth-adapter
  namespace: ingress-nginx
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
          securityContext:
            runAsUser: 1000
          name: ldap-auth-adapter
          ports:
            - name: http
              containerPort: 9000
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
  namespace: ingress-nginx
spec:
  type: ClusterIP
  selector:
    app: ldap-auth-adapter
  ports:
    - name: ldap-auth-adapter
      port: 80
      protocol: TCP
      targetPort: 9000
````
