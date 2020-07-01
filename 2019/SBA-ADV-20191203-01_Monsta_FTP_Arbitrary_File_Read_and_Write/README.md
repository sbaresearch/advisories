# Monsta FTP Arbitrary File Read and Write #

## Vulnerability Overview ##

Monsta FTP 2.10.1 or below allows external control of paths used in
filesystem operations. This allows attackers to read and write arbitrary
local files, allowing an attacker to gain remote code execution in
common deployments.

* **Identifier**            : SBA-ADV-20191203-01
* **Type of Vulnerability** : External Control of File Name or Path
* **Software/Product Name** : [Monsta FTP](https://www.monstaftp.com/)
* **Vendor**                : Monsta Limited
* **Affected Versions**     : <= 2.10.1
* **Fixed in Version**      : Not yet
* **CVE ID**                : CVE-2020-14057
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
* **CVSS Base Score**       : 9.8 (Critical)

## Vendor Description ##

> Monsta FTP is a web-based FTP client, developed in PHP & AJAX, you can
> use to manage your website through your browser, edit code, upload and
> download files, copy/move/delete files and folders - all without
> installing any desktop software.

Source: <https://www.monstaftp.com/>

## Impact ##

An unauthenticated attacker can read and write arbitrary local files
accessible by the webserver by exploiting the vulnerability documented
in this advisory. Sensitive data such as database credentials might get
exposed through this attack. Moreover, an attacker might gain remote
code execution by uploading PHP scripts in the web root and calling it via
the webserver.

## Vulnerability Description ##

*redacted*

## Proof of Concept ##

*redacted*

## Recommended Countermeasures ##

We are not aware of a vendor fix yet. Please contact the vendor.

*redacted*

## Timeline ##

* `2019-12-03`: identification of vulnerability in version 2.10
* `2019-12-10`: initial vendor contact
* `2019-12-14`: vendor released version 2.10.1
* `2019-12-14`: vendor response with security contact
* `2019-12-16`: first try to disclose vulnerability to vendor security contact
* `2020-01-13`: disclosed vulnerability to vendor security contact
* `2020-06-12`: re-test of vulnerability in version 2.10.1
* `2020-06-12`: request CVE from MITRE
* `2020-06-12`: MITRE assigned CVE-2020-14057
* `2020-07-01`: public disclosure with redacted technical details

## Credits ##

* David Gnedt ([SBA Research](https://www.sba-research.org/))
