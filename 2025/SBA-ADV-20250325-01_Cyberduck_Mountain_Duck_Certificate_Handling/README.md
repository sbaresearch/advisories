# Cyberduck and Mountain Duck - Improper Certificate Store Handling #

## Vulnerability Overview ##

Cyberduck and Mountain Duck improper handle TLS certificate pinning for
untrusted certificates (e.g., self-signed), unnecessarily installing it to the
*Windows Certificate Store* of the current user without any restrictions.
This potentially allows attackers to bypass certificate-based authentication
or authorization of other programs that trust this certificate store.

* **Identifier**            : SBA-ADV-20250325-01
* **Type of Vulnerability** : CWE-266: Incorrect Privilege Assignment
* **Software/Product Name** : [Cyberduck](https://cyberduck.io/) and [Mountain Duck](https://mountainduck.io/)
* **Vendor**                : [iterate GmbH](https://iterate.ch/)
* **Affected Versions**     : Cyberduck <= 9.1.6 and Mountain Duck <= 4.17.5
* **Fixed in Version**      : Cyberduck 9.1.7 and Mountain Duck 4.17.6
* **CVE ID**                : CVE-2025-41255
* **GHSA**                  : GHSA-vjjc-grpp-m655
* **CVSS Vector**           : CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N
* **CVSS Base Score**       : 8.0 (High)

## Vendor Description ##

> Cyberduck is a libre server and cloud storage browser for Mac and Windows
> with support for FTP, SFTP, WebDAV, Amazon S3, OpenStack Swift, Backblaze
> B2, Microsoft Azure & OneDrive, Google Drive and Dropbox.

Source: <https://cyberduck.io/>

> Mountain Duck lets you mount server and cloud storage as a disk in Finder
> on macOS and the File Explorer on Windows. Open remote files with any
> application and work like on a local volume.

Source: <https://mountainduck.io/>

## Impact ##

Other programs on the system that trust the *Windows Certificate Store* of
the current user can be attacked.
As the intended purpose of the certificate is not restricted, it can be
misused e.g., to perform server authentication, code signing or 
machine-in-the-middle attacks.

## Vulnerability Description ##

When permanently accepting an unknown TLS certificate for a specified
service, Cyberduck and Mountain Duck add the certificate to their own
configuration file and to the `Trusted Root Certification Authorities`
of the *Windows Certificate Store* of the current user, whereby its
`Intended Purposes` is set to `<All>`.
This means that all programs which trust the users *Windows Certificate
Store* also trust this certificate for all use cases.

## Proof of Concept ##

1. Setup a TLS encrypted *WebDAV* server, which uses a self-signed
certificate (in this case at the IP address `10.42.42.1`).

2. Create a new connection to the server in Cyberduck or Mountain Duck.

3. The following certificate error is shown, since the self-signed
certificate is not trusted: 
![Certificate error](./images/Certificate%20Error.png)  
To always trust this certificate for this connection, `Always Trust` must be
checked before clicking `Continue`.

4. Afterwards the following dialog shows up, asking if you want to install
the certificate:
![Security warning](./images/Security%20Warning.png)  
By clicking `No` the connection process gets canceled, therefore to continue
clicking `Yes` is required.

5. Now, the certificate is stored within the
`Trusted Root Certification Authorities` of the *Windows Certificate Store*
of the current user, whereby its `Intended Purposes` is set to `<All>`:
![Windows Certificate Store](./images/Windows%20Certificate%20Store.png)  
The thumbprint of the certificate is also stored at the configuration file
of the application:

Cyberduck (`C:\Users\<USER>\AppData\Roaming\Cyberduck\Cyberduck.user.config`):

```xml
<?xml version="1.0" encoding="utf-8"?><configuration><userSettings><Ch.Cyberduck.Properties.SharedSettings><setting name="Migrate" serializeAs="String"><value>False</value></setting><setting name="CdSettings" serializeAs="Xml"><value>
<settings>
  [...]
  <setting name="10.42.42.1.certificate.accept" value="88B16586B9EDF0F3A49663306BC4553289252909" />
  <setting name="bookmark.toggle.options" value="false" />
</settings></value></setting></Ch.Cyberduck.Properties.SharedSettings></userSettings></configuration>
```

Moutain Duck (`C:\Users\<USER>\AppData\Roaming\Cyberduck\Mountain Duck.user.config`):

```xml
<?xml version="1.0" encoding="utf-8"?><configuration><userSettings><Ch.Cyberduck.Properties.SharedSettings><setting name="Migrate" serializeAs="String"><value>False</value></setting><setting name="CdSettings" serializeAs="Xml"><value>
<settings>
  <setting name="bookmark.9e30b689-b7c6-40e1-90f1-fb090f77713d" value="0" />
  <setting name="session.9e30b689-b7c6-40e1-90f1-fb090f77713d" value="0" />
  <setting name="update.check.guid" value="a5fa3efc-8647-4a85-8d49-962e6c4cac77" />
  <setting name="10.42.42.1.certificate.accept" value="88B16586B9EDF0F3A49663306BC4553289252909" />
</settings></value></setting></Ch.Cyberduck.Properties.SharedSettings></userSettings></configuration>
```

This means that an attacker could, for example, use a phishing attack to
trick a victim into connecting to a server that uses a self-signed
certificate and is under the attacker's control. If the victim permanently
trusts the presented certificate for the specified connection, the
certificate is actually not only pinned for this specific connection,
but it is installed in the `Trusted Root Certification Authorities` of the
*Windows Certificate Store* of the current user, whereby its
`Intended Purposes` is set to `<All>`. This allows other programs on the
victim's system to be attacked.

## Recommended Countermeasures ##

We recommend to update to Cyberduck version 9.1.7 / Mountain Duck version
4.17.6 or later, which applies the following countermeasure.

When permanently accepting a TLS certificate for a specific service, the
application should store the certificate fingerprint only in its own
configuration file rather than installing the certificate in the Windows
Certificate Store. 
Since the certificate can be manually removed from the Windows Certificate
Store after installation and the applications do not display any certificate
errors, it seems that only the own configuration file is used to
verify pinned certificates anyway.
Adding the certificate to the *Windows Certificate Store* is therefore
apparently not necessary and only expands the system's attack surface
without any need.

## Timeline ##

* `2025-03-25` Identified the vulnerability in Cyberduck version 9.1.3
and Mountain Duck version 4.17.3
* `2025-03-27` Initial contact attempt and disclosure of vulnerability to
iterate GmbH via GitHub Security Advisory
* `2025-04-09` Vendor accepted this report
* `2025-06-20` Vendor created a private fork to address the problem
* `2025-06-23` Vendor merged the patch to main
* `2025-06-24` Vendor released Cyberduck 9.1.7 / Mountain Duck 4.17.6
* `2025-06-24` Public disclosure via GHSA
* `2025-06-25` SBA Research assigned CVE-2025-41255
* `2025-06-25` Public disclosure via CVE

## References ##

* GitHub Security Advisory. Cyberduck and Mountain Duck - Improper Certificate Store Handling: <https://github.com/iterate-ch/cyberduck/security/advisories/GHSA-vjjc-grpp-m655>

## Credits ##

* Andreas Boll ([SBA Research](https://www.sba-research.org/))
* Thomas Kostal ([SBA Research](https://www.sba-research.org/))