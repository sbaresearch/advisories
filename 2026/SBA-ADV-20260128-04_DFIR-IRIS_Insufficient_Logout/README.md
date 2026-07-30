# DFIR-IRIS Insufficient Logout Implementation #

## Vulnerability Overview ##

The IRIS web application in version 2.4.26 and possibly others contains a
logout functionality which is ineffective. Stolen session cookies can
therefore be misused for a long time.

* **Identifier**            : SBA-ADV-20260128-04
* **Type of Vulnerability** : Insufficient Logout Implementation
* **Software/Product Name** : [IRIS](https://www.dfir-iris.org/)
* **Vendor**                : [DFIR-IRIS](https://github.com/dfir-iris)
* **Affected Versions**     : 2.4.26
* **Fixed in Version**      : not currently available
* **CVE ID**                : CVE-2026-16970
* **CVSS Vector**           : CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N
* **CVSS Base Score**       : 4.2 (Medium)

## Vendor Description ##

> IRIS is a collaborative digital platform designed for incident response
> analysts to share complex investigations at a technical level. It can be
> installed on a dedicated server or as a portable application for roaming
> investigations where internet access might not be available.

Source: <https://docs.dfir-iris.org/2.4.24/>

## Impact ##

If a user logs out of the application, the session identifier will not be
invalidated on the server’s side. A stolen cookie can therefore be misused
even after a supposed logout has happened.

## Vulnerability Description ##

The logout implementation on the affected system does not provide a real
logout functionality. The logout function destroys the session only on the
client side. If the session cookie is known, an attacker can take over the
session.

## Proof of Concept ##

When clicking "Logout" in the application, there is a redirection to the
login page.

From the technical point of view, clicking “Logout” deletes the `session`
cookie in the browser and redirects to the logout page. However, the session
itself is still active on the server side. If an attacker gets hold of the
token in any way during the session, its validity cannot be terminated
prematurely.

An authenticated request to the web application looks like this:

```http
GET /user/tasks/list?cid= HTTP/1.1
Host: myiris.local
Cookie: session=.eJwt[...]Y-Rd7o
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
X-Requested-With: XMLHttpRequest
Referer: https://myiris.local/dashboard
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Te: trailers
Connection: keep-alive
```

The server returns the requested information:

```http
HTTP/1.1 200 OK
Server: nginx
Date: Mon, 26 Jan 2026 13:57:12 GMT
Content-Type: application/json
Content-Length: 622
Connection: keep-alive
Vary: Cookie
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

{"status": "success", "message": "", "data": {"tasks_status": [{"id": 1, "registry": null, "status_bscolor": "danger", "status_description": "", "status_name": "To do"}, {"id": 2, "registry": null, "status_bscolor": "warning", "status_description": "", "status_name": "In progress"}, {"id": 3, "registry": null, "status_bscolor": "muted", "status_description": "", "status_name": "On hold"}, {"id": 4, "registry": null, "status_bscolor": "success", "status_description": "", "status_name": "Done"}, {"id": 5, "registry": null, "status_bscolor": "muted", "status_description": "", "status_name": "Canceled"}], "tasks": []}}
```

After the successful request the user logs out of the application by sending
this request:

```http
GET /logout HTTP/1.1
Host: myiris.local
Cookie: session=.eJwt[...]Y-Rd7o
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://myiris.local/dashboard
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Priority: u=0, i
Te: trailers
Connection: keep-alive
```

The server answers with a redirect to the login page and instructs the
application to delete the session cookie:

```http hl:7,9
HTTP/1.1 302 FOUND
Server: nginx
Date: Mon, 26 Jan 2026 13:57:27 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 213
Connection: keep-alive
Location: /login?next=/
Vary: Cookie
Set-Cookie: session=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; Secure; HttpOnly; Path=/; SameSite=Lax
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/login?next=/">/login?next=/</a>. If not, click the link.
```

Now the server-side session should be deleted, but it is still possible to
request the same information as above with the old session cookie:

```http
GET /user/tasks/list?cid= HTTP/1.1
Host: myiris.local
Cookie: session=.eJwt[...]Y-Rd7o
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
X-Requested-With: XMLHttpRequest
Referer: https://myiris.local/dashboard
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Te: trailers
Connection: keep-alive

HTTP/1.1 200 OK
Server: nginx
Date: Mon, 26 Jan 2026 13:58:09 GMT
Content-Type: application/json
Content-Length: 622
Connection: keep-alive
Vary: Cookie
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

{"status": "success", "message": "", "data": {"tasks_status": [{"id": 1, "registry": null, "status_bscolor": "danger", "status_description": "", "status_name": "To do"}, {"id": 2, "registry": null, "status_bscolor": "warning", "status_description": "", "status_name": "In progress"}, {"id": 3, "registry": null, "status_bscolor": "muted", "status_description": "", "status_name": "On hold"}, {"id": 4, "registry": null, "status_bscolor": "success", "status_description": "", "status_name": "Done"}, {"id": 5, "registry": null, "status_bscolor": "muted", "status_description": "", "status_name": "Canceled"}], "tasks": []}}
```

This proofs that the session is still valid on the server side.

## Recommended Countermeasures ##

We are not aware of a fix yet. Please contact the vendor.

Clicking “Logout” should release the resources associated with the session
and cancel the session ID on the server side. Client-side deletion of the
current session cookie can also be done as an additional measure, but is
optional. Even with the formerly valid session ID, it should not be possible
to access the protected pages after clicking “Logout” without
re-authentication. Therefore, re-authentication must always be mandatory after
logout.

Stateless authentication tokens like *JSON Web Tokens (JWT)* are not intended
to be used as session tokens for precisely this reason.

## Timeline ##

* `2026-01-28` Identified the vulnerability in version 2.4.26
* `2026-01-30` Initial vendor contact attempt via e-mail
* `2026-02-27` Second vendor contact attempt via e-mail
* `2026-03-30` Report on GitHub due to a missing response from the vendor
* `2026-07-07` Informed project about imminent publication
* `2026-07-24` SBA assigned CVE number
* `2026-07-30` Public disclosure due to missing response from the vendor

## References ##

* OWASP Web Security Testing Guide (WSTG) v4.2. Testing for Logout
  Functionality:
  <https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/06-Session_Management_Testing/06-Testing_for_Logout_Functionality.html>
* OWASP Application Security Verification Standard (ASVS) v5.0.0. Requirement
  7.4.1 Verify that when session termination is triggered (such as logout or
  expiration), the application disallows any further use of the session:
  <https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/OWASP_Application_Security_Verification_Standard_5.0.0_en.pdf>
* OWASP Cheat Sheet Series. Session Management Cheat Sheet:
  <https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html>
* Common Weakness Enumeration. CWE-613 Insufficient Session Expiration:
  <https://cwe.mitre.org/data/definitions/613.html>

## Credits ##

* Michael Koppmann ([SBA Research](https://www.sba-research.org/))
* Mathias Tausig ([SBA Research](https://www.sba-research.org/))

The discovery of this vulnerability was made possible through support from
[CYSSDE](https://cyssde.eu/) and the European Union.

![CYSSDE](images/cyssde.png)
