# Filebrowser Sensitive Data Transferred in URL #

## Vulnerability Overview ##

URLs that are accessed by a user are commonly logged in many locations, both
server- and client-side. It is thus good practice to never transmit any
secret information as part of a URL. Filebrowser violates this
practice, since access tokens are used as GET parameters.

* **Identifier**            : SBA-ADV-20250327-03
* **Type of Vulnerability** : Information Disclosure
* **Software/Product Name** : [Filebrowser](https://filebrowser.org/)
* **Vendor**                : [Filebrowser](https://github.com/filebrowser)
* **Affected Versions**     : <= 2.33.8
* **Fixed in Version**      : 2.33.9
* **CVE ID**                : CVE-2025-52901
* **CVSS Vector**           : CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N
* **CVSS Base Score**       : 4.5 (Medium)

## Vendor Description ##

> filebrowser provides a file managing interface within a specified directory
> and it can be used to upload, delete, preview, rename and edit your files.
> It allows the creation of multiple users and each user can have its own
> directory. It can be used as a standalone app.

Source: <https://github.com/filebrowser/filebrowser/blob/v2.32.0/README.md>

## Impact ##

The *JSON Web Token (JWT)* which is used as a session identifier will get
leaked to anyone having access to the URLs accessed by the user. This will
give the attacker full access to the user's account and, in consequence, to
all sensitive files the user has access to.

## Vulnerability Description ##

Sensitive information in URLs is logged by several components (see the
following examples), even if access is protected by TLS.

* The browser history
* The access logs on the affected web server
* Proxy servers or reverse proxy servers
* Third-party servers via the HTTP referrer header

In case attackers can access certain logs, they could read the included
sensitive data.

## Proof of Concept ##

When a file is downloaded via the web interface, the JWT is part of the URL:

```http
GET /api/raw/testdir/testfile.txt?auth=eyJh[...]_r4EQ HTTP/1.1
Host: filebrowser.local:8080
Referer: http://filebrowser.local:8080/files/testdir/
Cookie: auth=eyJh[...]_r4EQ
[...]
```

This also happens when a new *command session* is started:

```http
GET /api/command/?auth=eyJh[...]YW8BA HTTP/1.1
Host: filebrowser.local:8080
Sec-WebSocket-Version: 13
Origin: http://filebrowser.local:8080
Sec-WebSocket-Key: oqQMrF7R34D3lAkj1+ZHTw==
Cookie: auth=eyJh[...]YW8BA
Upgrade: websocket
[...]
```

## Recommended Countermeasures ##

Sensitive data like session tokens or user credentials should be transmitted
via HTTP headers or the HTTP body only, never in the URL.

## Timeline ##

* `2025-03-27` Identified the vulnerability in version 2.32.0
* `2025-04-11` Contacted the project
* `2025-04-29` Vulnerability disclosed to the project
* `2025-06-25` Uploaded advisories to the project's GitHub repository
* `2025-06-26` CVE ID assigned by GitHub
* `2025-06-26` Fix released with version 2.33.9
* `2025-06-26` Advisory published by project as `GHSA-rmwh-g367-mj4x`

## References ##

* CWE-598: Use of GET Request Method With Sensitive Query Strings: <https://cwe.mitre.org/data/definitions/598.html>
* GitHub Security Advisory: <https://github.com/filebrowser/filebrowser/security/advisories/GHSA-rmwh-g367-mj4x>

## Credits ##

* Mathias Tausig ([SBA Research](https://www.sba-research.org/))
