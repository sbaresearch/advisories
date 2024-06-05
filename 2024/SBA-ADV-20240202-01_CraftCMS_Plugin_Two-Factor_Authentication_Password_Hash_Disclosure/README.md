# CraftCMS Plugin - Two-Factor Authentication - Password Hash Disclosure #

## Vulnerability Overview ##

The CraftCMS plugin Two-Factor Authentication in versions 3.3.1, 3.3.2 and
3.3.3 discloses the password hash of the currently authenticated user after
submitting a valid TOTP.

* **Identifier**            : SBA-ADV-20240202-01
* **Type of Vulnerability** : Exposure of Sensitive Attributes
* **Software/Product Name** : [Two-Factor Authentication](https://plugins.craftcms.com/two-factor-authentication?craft4)
* **Vendor**                : [Born05](https://www.born05.com/en/)
* **Affected Versions**     : 3.3.1, 3.3.2 and 3.3.3
* **Fixed in Version**      : 3.3.4
* **CVE ID**                : CVE-2024-5657
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N
* **CVSS Base Score**       : 3.7 (Low)

## Vendor Description ##

> Craft 4 plugin for two-factor or two-step login using Time Based OTP (TOTP,
> like Google Authenticator).

Source: <https://github.com/born05/craft-twofactorauthentication>

## Impact ##

Assuming that an attacker obtains the session of a victim. Then, the attacker
is able to retrieve the password-hash of the victim, which constitues an
authorization vulnerability. In general, users should not even be able to
read their own password hashes. In the worst case the attacker is able to
obtain the cleartext password by cracking the password hash. Then, the
attacker can disable MFA from within the hijacked session and consecutively
establish new sessions in the context of the victim.

## Vulnerability Description ##

After submitting the `authenticationCode`, the server responds in case of
success, with the password hash of the authenticated user. The
`authenticationCode` is the time-based one-time password associated with the
authenticatd user. This `authenticationCode` can be submitted on at least the
following endpoints:

1. `/index.php?p=admin%2Factions%2Ftwo-factor-authentication%2Fsettings%2Fturn-on`
2. `/index.php?p=admin%2Factions%2Ftwo-factor-authentication%2Fverify%2Flogin-process`

The first endpoint is used to enroll a second factor, while the second
endpoint is used in the authentication process to verify the second factor.

A user who has two factor authentication enabled is not protected from this
attack, since two factor authentication can be disabled and re-enrolled
without entering a password. After re-enrolling the attack will obtain the
password-hash. The HTTP response that contains the password-hash has the HTTP
header `Cache-Control: no-cache, no-store, must-revalidate` set, meaning, the
browser does not cache the response.

Due to the disclosure of the password hash, there is the possibility that the
attacker is able to prolong the access to the account beyond the lifetime of
a single session obtained from the victim. Furthermore, the attacker might
use the password in credential stuffing attacks against other services.

## Proof of Concept ##

Assuming that an attacker is in control of the session of a victim.

If the victim has two factor authentication enabled, the attacker can disable
it. The plugin then reveals a newly generated shared secret which the
attacker can use to calculate the current one-time password. With the
following request the attacker reenables two factor authentication.

```http
POST /index.php?p=admin%2Factions%2Ftwo-factor-authentication%2Fsettings%2Fturn-on HTTP/1.1
Host: example.com
Cookie: CraftSessionId=[...];
[...]

{
    "authenticationCode": "123456"
}
```

If the `authenticationCode` is a valid TOTP, the server returns a response
containing the password hash of the victim.

```http
HTTP/1.1 200 OK
[...]

{
    [...]
    "user": {
        "password": "$2y$13$[...]",
        [...]
    }
}
```

## Recommended Countermeasures ##

We recommend to update to version 3.3.4 or later, which applies the following
countermeasure.

We suggest to never disclose the password hash to the user.

## Timeline ##

* `2024-02-02`: Identified the vulnerability in version 3.3.2
* `2024-02-04`: Contacted the Maintainer
* `2024-02-05`: Vulnerability disclosed to the Maintainer
* `2024-02-07`: Requested CVE from MITRE
* `2024-02-08`: Maintainer released version 3.3.3 which is still vulnerable
* `2024-02-08`: Maintainer fixed the vulnerability in version 3.3.4
* `2024-06-04`: SBA Research becomes a CNA
* `2024-06-05`: SBA Research assigned CVE-2024-5657
* `2024-06-06`: Public disclosure

## References ##

* Advisory regarding a similar vulnerability in CraftCMS (CVE-2022-37783): <https://at-trustit.tuvaustria.com/tuev-trust-it-cves/cve-disclosure-of-password-hashes/>

## Credits ##

* Fabian Funder ([SBA Research](https://www.sba-research.org/))
* Jakob Pachmann ([SBA Research](https://www.sba-research.org/))
