# Filebrowser Insecure File Permissions #

## Vulnerability Overview ##

The file access permissions for files uploaded to or created from Filebrowser
are never explicitly set by the application. The same is true for the
database used by Filebrowser. On standard servers where the *umask*
configuration has not been hardened before, this makes all the stated files
readable by any operating system account.

* **Identifier**            : SBA-ADV-20250325-03
* **Type of Vulnerability** : Incorrect Default Permissions
* **Software/Product Name** : [Filebrowser](https://filebrowser.org/)
* **Vendor**                : [Filebrowser](https://github.com/filebrowser)
* **Affected Versions**     : <= 2.33.6
* **Fixed in Version**      : 2.33.7
* **CVE ID**                : CVE-2025-52900
* **CVSS Vector**           : CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N
* **CVSS Base Score**       : 5.5 (Medium)

## Vendor Description ##

> filebrowser provides a file managing interface within a specified directory
> and it can be used to upload, delete, preview, rename and edit your files.
> It allows the creation of multiple users and each user can have its own
> directory. It can be used as a standalone app.

Source: <https://github.com/filebrowser/filebrowser/blob/v2.32.0/README.md>

## Impact ##

The default permissions for new files on a standard Linux system are `0644`,
making them world-readable. That means that at least the following parties
have full read access to all files managed by the Filebrowser from all
*scopes*, as well as its database (including the password hashes stored in
there):

* All OS accounts on the server
* All other applications running on the same server
* Any Filebrowser user with *Command Execution* privileges having access to a
  command that allows reading a file's content

## Vulnerability Description ##

On a Linux system, the file access permissions of new files are designated by
the system-wide *umask* setting, unless they are configured manually. Most
distributions set this value to `022` by default which gives every account
on the system read permissions on the file.

```bash
$ umask
022
$ touch foo
$ ls -l foo
-rw-r--r-- 1 sba sba 0 31. Mär 15:08 foo
```

## Proof of Concept ##

Upload or create a file in the Filebrowser GUI and list the directory
contents from a shell:

```bash
$ ls -l /srv/filebrowser/testdir
total 12
-rw-r--r-- 1 sba sba 7703 Mar 25 16:07 dummy1.pdf
-rw-r--r-- 1 sba sba    3 Mar 25 15:46 testfile.txt
```

The same can be validated for Docker based deployments within the container:

```bash
$ docker exec -it e0f075082a2c ls /srv/testdir -l
total 12
-rw-r--r--    1 1000     1000          7703 Mar 25 15:07 dummy1.pdf
-rw-r--r--    1 1000     1000             3 Mar 25 14:46 testfile.txt
```

Furthermore, the database used by the Filebrowser application is readable by
any account:

```bash
$ ls -l /srv/filebrowser/filebrowser.db 
-rw-rw-r-- 1 sba sba 65536 Mar 25 09:58 /srv/filebrowser/filebrowser.db
```

## Recommended Countermeasures ##

Since the system's *umask* configuration cannot be controlled by the
Filebrowser, the application needs to set the permissions of all new files
manually upon creation. No permissions should be given to the *other*
category.

Implementing this won't fix the permissions for active instances after an
update, so site administrators will need to fix the permissions manually:

```bash
$ chmod o-rwx -R /srv/filebrowser/datadir
```

## Timeline ##

* `2025-03-25` Identified the vulnerability in version 2.32.0
* `2025-04-11` Contacted the project
* `2025-04-18` Vulnerability disclosed to the project
* `2025-06-25` Uploaded advisories to the project's GitHub repository
* `2025-06-26` CVE ID assigned by GitHub
* `2025-06-26` Fix released with version 2.33.7
* `2025-06-26` Advisory published by project as `GHSA-jj2r-455p-5gvf`

## References ##

* CWE-276: Incorrect Default Permissions: <https://cwe.mitre.org/data/definitions/276.html>
* What is Umask and How To Setup Default umask Under Linux?: <https://www.cyberciti.biz/tips/understanding-linux-unix-umask-value-usage.html>
* GitHub Security Advisory: <https://github.com/filebrowser/filebrowser/security/advisories/GHSA-jj2r-455p-5gvf>

## Credits ##

* Mathias Tausig ([SBA Research](https://www.sba-research.org/))
