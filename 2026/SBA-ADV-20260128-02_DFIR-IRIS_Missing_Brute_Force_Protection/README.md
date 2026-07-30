# DFIR-IRIS Missing Brute Force Protection #

## Vulnerability Overview ##

The IRIS web application in version 2.4.26 and possibly others does not
protect its MFA validation (CVE-2026-16971) and user authentication
(CVE-2026-18362) against brute-force attacks.

* **Identifier**            : SBA-ADV-20260128-02
* **Type of Vulnerability** : Missing Brute Force Protection
* **Software/Product Name** : [IRIS](https://www.dfir-iris.org/)
* **Vendor**                : [DFIR-IRIS](https://github.com/dfir-iris)
* **Affected Versions**     : 2.4.26
* **Fixed in Version**      : not currently available
* **CVE IDs**               : CVE-2026-16971 CVE-2026-18362
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N
* **CVSS Base Score**       : 5.9 (Medium)

## Vendor Description ##

> IRIS is a collaborative digital platform designed for incident response
> analysts to share complex investigations at a technical level. It can be
> installed on a dedicated server or as a portable application for roaming
> investigations where internet access might not be available.

Source: <https://docs.dfir-iris.org/2.4.24/>

## Impact ##

There is no observable rate-limiting for the endpoints which validate a
user’s password or OTP. This means that brute-force attacks on a user’s
password are possible and MFA must be considered ineffective.

## Vulnerability Description ##

The affected system does not implement sufficient restrictions on resources
and requests. This creates the potential for a brute force attack on
authentication endpoints.

## Proof of Concept ##

### OTP Validation (CVE-2026-16971) ###

The following request is sent to the application if the user enters a
*One-time Password (OTP)* to complete the *Multi-factor Authentication (MFA)*:

```http
POST /auth/mfa-verify HTTP/1.1
Host: myiris.local
Cookie: session=.eJwd[...]
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded
Content-Length: 110
Origin: https://myiris.local
Referer: https://myiris.local/auth/mfa-verify
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Priority: u=0, i
Te: trailers
Connection: keep-alive

csrf_token=IjZjMWQ5YWZiOTg4MDQyZDBkMGFhNzMwYWIyOTBkNTFkZGMxYTJiM2Ei.aWTb9g.CqozcZ7VxJNwjX0VCwq4MZe1i_k&token=123456

HTTP/1.1 200 OK
Server: nginx
Date: Mon, 26 Jan 2026 11:33:23 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 4223
Connection: keep-alive
Vary: Cookie
Set-Cookie: session=.eJyd[...]; Secure; HttpOnly; Path=/; SameSite=Lax
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

[...]
```

Note that the response code of the application indicates a success (`200 OK`)
even if an incorrect OTP has been sent. A valid OTP causes a redirect:

```http
HTTP/1.1 302 FOUND
Server: nginx
Date: Mon, 26 Jan 2026 11:32:45 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 219
Connection: keep-alive
Location: /dashboard?cid=1
Vary: Cookie
Set-Cookie: session=.eJw1[...]; Secure; HttpOnly; Path=/; SameSite=Lax
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
<p>You should be redirected automatically to the target URL: <a href="/dashboard?cid=1">/dashboard?cid=1</a>. If not, click the link.
```

During the test the whole possible space of valid OTPs (6 digits, 1 million
possibilities) was sent to the application in quick succession. No delay or
account lockout was observed, the user could still authenticate with the
correct OTP afterwards.

Since the space of possible values is so small for OTPs, this effectively
constitutes a bypass of the MFA policy.

### User Authentication (CVE-2026-18362) ###

No limitation of any kind was observed when performing a brute-force attack
on an account’s password. Neither were the requests delayed or blocked, nor
was the user’s account locked.

## Recommended Countermeasures ##

We are not aware of a fix yet. Please contact the vendor.

We recommend implementing a generic solution that allows context-dependent
rate limiting to be applied at least

* per source (e.g., IP address),
* per subject (e.g., account or session),
* per object (e.g., queried database entry), and
* per time (e.g., one minute)

is allowed. For example, this can be implemented in the form of an annotation
that allows different limits per action. It is common to return the HTTP
error code 429 “Too Many Requests” if the limit is exceeded.

It is important that not only further requests are blocked when the limit is
exceeded, but to also log the exceeding ones.

Especially sensitive endpoints used for authentication purposes need a
dedicated protection against brute-force attacks.

## Timeline ##

* `2026-01-28` Identified the vulnerability in version 2.4.26
* `2026-01-30` Initial vendor contact attempt via e-mail
* `2026-02-27` Second vendor contact attempt via e-mail
* `2026-03-30` Report on GitHub due to a missing response from the vendor
* `2026-07-07` Informed project about imminent publication
* `2026-07-24` SBA assigned CVE number
* `2026-07-30` SBA assigned additional CVE numbers since the instances are
               independently fixable
* `2026-07-30` Public disclosure due to missing response from the vendor

## References ##

* OWASP API Security Top 10 2023. API4:2023 Unrestricted Resource Consumption:
  <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>
* Common Weakness Enumeration. CWE-770 Allocation of Resources Without Limits
  or Throttling: <https://cwe.mitre.org/data/definitions/770.html>

## Credits ##

* Michael Koppmann ([SBA Research](https://www.sba-research.org/))
* Mathias Tausig ([SBA Research](https://www.sba-research.org/))

The discovery of this vulnerability was made possible through support from
[CYSSDE](https://cyssde.eu/) and the European Union.

![CYSSDE](images/cyssde.png)
