# Monsta FTP Stored Cross-Site Scripting #

## Vulnerability Overview ##

Monsta FTP 2.10.1 or below is prone to a stored cross-site scripting
vulnerability in the language setting due to insufficient output encoding.

* **Identifier**            : SBA-ADV-20191211-01
* **Type of Vulnerability** : Cross Site Scripting
* **Software/Product Name** : [Monsta FTP](https://www.monstaftp.com/)
* **Vendor**                : Monsta Limited
* **Affected Versions**     : <= 2.10.1
* **Fixed in Version**      : Not yet
* **CVE ID**                : CVE-2020-14055
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N
* **CVSS Base Score**       : 8.2 (High)

## Vendor Description ##

> Monsta FTP is a web-based FTP client, developed in PHP & AJAX, you can
> use to manage your website through your browser, edit code, upload and
> download files, copy/move/delete files and folders - all without
> installing any desktop software.

Source: <https://www.monstaftp.com/>

## Impact ##

By exploiting the documented vulnerabilities, an unauthenticated attacker
can store JavaScript code on the server. The Monsta FTP instance
delivers the JavaScript code to each user, which is then executed in the
user's browser within the origin of the Monsta FTP instance.
This might lead to information leakage like FTP credentials and can also
affect other applications running within the same origin.

## Vulnerability Description ##

*redacted*

## Proof of Concept ##

*redacted*

## Recommended Countermeasures ##

We are not aware of a vendor fix yet. Please contact the vendor.

*redacted*

## Timeline ##

* `2019-12-10`: initial vendor contact
* `2019-12-11`: identification of vulnerability in version 2.10
* `2019-12-14`: vendor released version 2.10.1
* `2019-12-14`: vendor response with security contact
* `2019-12-16`: first try to disclose vulnerability to vendor security contact
* `2020-01-13`: disclosed vulnerability to vendor security contact
* `2020-06-12`: re-test of vulnerability in version 2.10.1
* `2020-06-12`: request CVE from MITRE
* `2020-06-12`: MITRE assigned CVE-2020-14055
* `2020-07-01`: public disclosure with redacted technical details

## Credits ##

* David Gnedt ([SBA Research](https://www.sba-research.org/))
