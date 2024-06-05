# CraftCMS Plugin - Two-Factor Authentication - TOTP Token Stays Valid After Use #

## Vulnerability Overview ##

The CraftCMS plugin Two-Factor Authentication through 3.3.3 allows reuse of
TOTP tokens multiple times within the validity period.

* **Identifier**            : SBA-ADV-20240202-02
* **Type of Vulnerability** : Improper Authentication
* **Software/Product Name** : [Two-Factor Authentication](https://plugins.craftcms.com/two-factor-authentication?craft4)
* **Vendor**                : [Born05](https://www.born05.com/en/)
* **Affected Versions**     : <= 3.3.3
* **Fixed in Version**      : 3.3.4
* **CVE ID**                : CVE-2024-5658
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N
* **CVSS Base Score**       : 4.8 (Medium)

## Vendor Description ##

> Craft 4 plugin for two-factor or two-step login using Time Based OTP (TOTP,
> like Google Authenticator).

Source: <https://github.com/born05/craft-twofactorauthentication>

## Impact ##

An attacker who is in possession of an TOTP token is able to establish an
authenticated session. This requires that the attacker has knowledge of the
victim's credentials.

## Vulnerability Description ##

A TOTP token can be used multiple times to establish an authenticated session.
RFC 6238 insists that an OTP must not be used more than once [1].

> The verifier MUST NOT accept the second attempt of the OTP after the
> successful validation has been issued for the first OTP, which ensures
> one-time only use of an OTP.

The OWASP Application Security Verification Standard v4.0.3 (ASVS) reiterates
this property with requirement 2.8.4 [2].

> Verify that time-based OTP can be used only once within the validity period.

## Proof of Concept ##

Start the login process in two different environments e.g. in two different
browsers. Enter the same TOTP in both environments while making sure that
both submissions are made in the timespan where the TOTP is valid. Both
environments should display the dashboard, signaling that the authentication
process has been successful.

The following request and response pairs show this behavior. The requests are
made from different session (different `CraftSessionId` and `identity`
cookie), but yield the same response. Therefore, the one-time use requirement
of TOTPs has been shown to be violated.

Request and response 1:

```http
POST /index.php?p=admin%2Factions%2Ftwo-factor-authentication%2Fverify%2Flogin-process HTTP/1.1
Host: example.org
Cookie: dc06c534a0efbcbec00d44ec8b36ae7a_identity=7facf57ff[...]; CraftSessionId=3f8122e456[...]
[...]

{"authenticationCode":"317415"}


HTTP/1.1 200 OK
Date: Tue, 06 Feb 2024 11:09:23 GMT
[...]

{
    "returnUrl":"https://example.org/admin/dashboard",
    [...]
}
```

Request and response 2:

```http
POST /index.php?p=admin%2Factions%2Ftwo-factor-authentication%2Fverify%2Flogin-process HTTP/1.1
Host: example.org
Cookie: dc06c534a0efbcbec00d44ec8b36ae7a_identity=830fcd6c62[...]; CraftSessionId=3fbfbf904c[...]

{"authenticationCode":"317415"}


HTTP/1.1 200 OK
Date: Tue, 06 Feb 2024 11:09:25 GMT
[...]

{
    "returnUrl":"https://example.org/admin/dashboard",
    [...]
}
```

## Recommended Countermeasures ##

We recommend to update to version 3.3.4 or later, which applies the following
countermeasure.

We suggest that TOTPs should loose their validity after they have been used.
In order to accomplish this a blocklist could be implemented where TOTPs used
by a particular user are logged. This list must be periodically cleaned up to
prevent collisions.

## Timeline ##

* `2024-02-02`: Identified the vulnerability in version 3.3.2
* `2024-02-04`: Contacted the Maintainer
* `2024-02-05`: Vulnerability disclosed to the Maintainer
* `2024-02-07`: Requested CVE from MITRE
* `2024-02-08`: Maintainer released version 3.3.3 which is still vulnerable
* `2024-02-08`: Maintainer fixed the vulnerability in version 3.3.4
* `2024-06-04`: SBA Research becomes a CNA
* `2024-06-05`: SBA Research assigned CVE-2024-5658
* `2024-06-06`: Public disclosure

## References ##

1. RFC 6238. TOTP Time-Based One-Time Password Algorithm: <https://www.rfc-editor.org/rfc/rfc6238>
2. OWASP Application Security Verification Standard (ASVS) v4.0.3. Requirement 2.8.4 Verify that time-based OTP can be used only once within the validity period: <https://github.com/OWASP/ASVS/blob/v4.0.3/4.0/en/0x11-V2-Authentication.md#v28-one-time-verifier>

## Credits ##

* Fabian Funder ([SBA Research](https://www.sba-research.org/))
* Jakob Pachmann ([SBA Research](https://www.sba-research.org/))
