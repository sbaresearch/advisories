# Polycom BToE Connector Privilege Escalation Vulnerability #

## Vulnerability Overview ##

Polycom BToE Connector up to version 2.3.0 allows unprivileged windows
users to execute arbitrary code with SYSTEM privileges.

* **Identifier**            : Polycom_20150513
* **Type of Vulnerability** : Privilege Escalation
* **Exploitation Vector**   : local
* **Software/Product Name** : Polycom BToE Connector
* **Vendor**                : Polycom Inc.
* **Affected Versions**     : All Version including 2.3.0
* **Fixed in Version**      : Versions 3.0.0 (Released March 2015)
* **CVE ID**                : CVE-2015-8300
* **CVSSv2 Vector**         : (AV:L/AC:L/Au:S/C:C/I:C/A:N)
* **CVSSv2 Base Score**     : 6.2

## Impact ##

Code execution with SYSTEM privileges.

## Vulnerability Description ##

The Polycom BToE Connector Version up to version 2.3.0 allows a local
user to gain local administrator privileges.

The software creates a windows service running with SYSTEM privileges
using the following file (standard installation path):

```text
C:\program files (x86)\polycom\polycom btoe connector\plcmbtoesrv.exe
```

The default installation allows everyone to replace the `plcmbtoesrv.exe`
file allowing unprivileged users to execute arbitrary commands on the
windows host.

## Proof-of-Concept ##

*none*

## Timeline ##

* `2014-12-19` identification of vulnerability
* `2015-01-01` vendor contacted via customer
* `2015-03-01` vendor released fixed version 3.0.0
* `2015-07-14` contact cve-request@mitre.

## References ##

* Download secure version 3.0.0 <http://support.polycom.com/PolycomService/support/us/support/eula/ucs/UCagreement_BToE_3_0_0.html>

## Credits ##

* Severin Winkler ([SBA Research](https://www.sba-research.org/))
* Ulrich Bayer ([SBA Research](https://www.sba-research.org/))
