# SQL Injection Vulnerability in RXTEC RXAdmin #

## Vulnerability Overview ##

SQL injection vulnerability in the RXTEC RXAdmin Login Page allows
remote attackers to execute arbitrary SQL commands via several HTTP
parameter.

* **Identifier**            : RXTEC_20150513
* **Type of Vulnerability** : SQL injection
* **Software/Product Name** : RXTEC RXAdmin Login
* **Vendor**                : RXTEC (www.rxtec.net)
* **Affected Versions**     : UPDATE : 06 / 2012
* **Fixed in Version**      : *unknown*
* **CVE ID**                : CVE-2015-8298
* **Impact**                : Critical

## Impact ##

It is possible to extract all information from the database in use by
the application. Depending on the configuration of the SQL server
arbitrary code execution might be possible.

## Vulnerability Description ##

The following parameters are affectey by the vulnerability:

* `/index.htm` (loginpassword parameter)
* `/index.htm` (loginusername parameter)
* `/index.htm` (zusätzlicher parameter)
* `/index.htm` (zusätzlicher parameter)
* `/index.htm` (rxtec cookie)
* `/index.htm` (groupid parameter)

## Proof-of-Concept ##

*none*

## Timeline ##

* `2015-04-30` identification of vulnerability
* `2015-05-11` vendor contact (won't fix because of outdated version)
* `2015-07-14` contact cve-request@mitre.

## Credits ##

* Thomas Konrad ([SBA Research](https://www.sba-research.org/))
