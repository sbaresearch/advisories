# Craft CMS - TOTP Token Stays Valid After Use #

## Vulnerability Overview ##

The Craft CMS from version 5.0.0-beta.1 through 5.2.2 allows reuse of TOTP tokens multiple times within the
validity period.

* **Identifier**            : SBA-ADV-20240617-01
* **Type of Vulnerability** : Improper Authentication
* **Software/Product Name** : [Craft CMS](https://craftcms.com)
* **Vendor**                : [Pixel & Tonic, Inc.](https://pixelandtonic.com)
* **Affected Versions**     : >= 5.0.0-beta.1, <= 5.2.2
* **Fixed in Version**      : 5.2.3
* **CVE ID**                : CVE-2024-41800
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N
* **CVSS Base Score**       : 4.8 (Medium)

## Vendor Description ##

> Craft is a flexible, user-friendly CMS for creating custom digital
> experiences on the web and beyond.

Source: <https://github.com/craftcms/cms>

## Impact ##

An attacker is able to re-submit a valid TOTP token to establish an
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

It should also be noted that the validity period of an TOTP token is 2
minutes. This makes a successful brute force attack more likely, since the
four tokens are valid at the same time.

## Proof of Concept ##

Start the login process in two different environments e.g. in two different
browsers. Enter the same TOTP in both environments while making sure that
both submissions are made in the timespan where the TOTP is valid. Both
environments should display the dashboard, signaling that the authentication
process has been successful.

The following request and response pairs show this behavior. The requests are
made from different session (different `CraftSessionId` cookie), but yield
the same response. Therefore, the one-time use requirement of TOTPs has been
shown to be violated.

Request and response 1:

```http
POST /index.php?p=admin%2Factions%2Fauth%2Fverify-totp&v=1718611475335 HTTP/1.1
Host: example.com
Cookie: CraftSessionId=f52a55[...]; CRAFT_CSRF_TOKEN=84046fab20[...]; b355f5550c68c4120bf669f0e80588c6_username=677791f5[...];
X-Requested-With: XMLHttpRequest
X-Csrf-Token: 3jS9tkBnKBRDJ[...]
Content-Length: 17
Connection: close

{"code":"101472"}

HTTP/1.1 200 OK
Content-Type: application/json; charset=UTF-8
Date: Mon, 17 Jun 2024 08:04:35 GMT
[...]

{"message":"Verification successful."}
```

Request and response 2:

```http
POST /index.php?p=admin%2Factions%2Fauth%2Fverify-totp&v=1718611477246 HTTP/1.1
Host: example.com
Cookie: CraftSessionId=221f47[...]; CRAFT_CSRF_TOKEN=2db430[...]; b355f5550c68c4120bf669f0e80588c6_username=677791[...];
X-Requested-With: XMLHttpRequest
X-Csrf-Token: Raz6Fv[...]
Content-Length: 17
Connection: close

{"code":"101472"}

HTTP/1.1 200 OK
Content-Type: application/json; charset=UTF-8
Date: Mon, 17 Jun 2024 08:04:37 GMT

[...]

{"message":"Verification successful."}
```

## Recommended Countermeasures ##

We recommend to update to version 5.2.3 or later, which applies the following
countermeasure.

We suggest that TOTPs should loose their validity after they have been used
and only newer token should be accepted. The `Google2FA` library which is
already in use provides such a functionality [3]:

> An attacker might be able to watch the user entering his credentials and
> one time key. Without further precautions, the key remains valid until it
> is no longer within the window of the server time. In order to prevent
> usage of a one time key that has already been used, you can utilize the
> `verifyKeyNewer` function.

## Timeline ##

* `2024-06-17`: Identified the vulnerability in version 5.1.8
* `2024-06-17`: Contacted the vendor and disclosed the vulnerability
* `2024-06-20`: Started to collaborate with the vendor on a Github Security Advisory (GHSA)
* `2024-06-20`: Release of fixed version 5.2.3
* `2024-07-25`: Public disclosure of GHSA
* `2024-07-25`: Public disclosure of SBA-ADV

## References ##

1. RFC 6238. TOTP Time-Based One-Time Password Algorithm: <https://www.rfc-editor.org/rfc/rfc6238>
2. OWASP Application Security Verification Standard (ASVS) v4.0.3. Requirement 2.8.4 Verify that time-based OTP can be used only once within the validity period: <https://github.com/OWASP/ASVS/blob/v4.0.3/4.0/en/0x11-V2-Authentication.md#v28-one-time-verifier>
3. Google2FA. Validation Window: <https://github.com/antonioribeiro/google2fa?tab=readme-ov-file#validation-window>
4. GitHub Security Advisory. TOTP Token Stays Valid After Use: <https://github.com/craftcms/cms/security/advisories/GHSA-wmx7-pw49-88jx>

## Credits ##

* Fabian Funder ([SBA Research](https://www.sba-research.org/))
