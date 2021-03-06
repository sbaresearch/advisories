# WordPress Plugin - Events Manager - Stored XSS #

## Vulnerability Overview ##

The events-manager plugin through 5.9.5 for WordPress (aka Events Manager)
is susceptible to Stored XSS due to improper encoding and insertion of
data provided to the attribute map_style of shortcodes (locations_map
and events_map) provided by the plugin.

* **Identifier**            : SBA-ADV-20190913-03
* **Type of Vulnerability** : Cross-site Scripting
* **Software/Product Name** : [Events Manager](https://wordpress.org/plugins/events-manager/)
* **Vendor**                : [Marcus Sykes](https://wp-events-plugin.com)
* **Affected Versions**     : <= 5.9.5
* **Fixed in Version**      : 5.9.6
* **CVE ID**                : CVE-2019-16523
* **CVSSv3 Vector**         : AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N
* **CVSSv3 Base Score**     : 7.3 (High)

## Vendor Description ##

> Events Manager is a full-featured event registration plugin for WordPress based on the principles of flexibility, reliability and powerful features!
>
> Version 5 now makes events and locations WordPress Custom Post Types, allowing for more possibilities than ever before!

Active Installations: 100,000+

Source: <https://wordpress.org/plugins/events-manager/>

## Impact ##

By exploiting the documented vulnerability, an authenticated attacker with the
ability to create posts can execute JavaScript code in a victim's browser.
This can be misused, e.g for phishing attacks by displaying a fake
login form and sending the victim's credentials to the attacker.
Furthermore malicious actions can be performed in the context of an authenticated
user. The impact depends on the level of access of the attacked user.
In case of an admin this can lead to the execution of PHP code and the compromise
of the server.

## Vulnerability Description ##

The plugin provides [*shortcodes*][1] to create a map widget e.g. for displaying the
location of an event. Those maps can be visually adjusted by providing
a custom style via the attribute `map_style` in the shortcode. The usage of HTML inside
shortcode attributes is [limited][2] in order to prevent XSS.
However in this case it is possible to inject arbitrary HTML and JavaScript because the
`map_style` attribute expects a base64-encoded JSON-object. This allows bypassing sanitization.
The shortcodes `locations_map` and `events_map` are affected by this problem:

In `em-shortcode.php` (line 43-56) we can see that the attribute is base64-decoded and then
parsed with json_decode. If the JSON syntax is valid, whitespace is removed and the object
passed to the template as `map_json_style` variable. See the code snippet below:

```php
//add JSON style to map
$style = '';
if( !empty($args['map_style']) ){
    $style= base64_decode($args['map_style']);
    $style_json= json_decode($style);
    if( is_array($style_json) || is_object($style_json) ){
        $style = preg_replace('/[\r\n\t\s]/', '', $style);
    }else{
        $style = '';
    }
    unset($args['map_style']);
}
ob_start();
em_locate_template('templates/map-global.php',true, array('args'=>$args, 'map_json_style' => $style));
```

In `templates/templates/map-global.php` (line 16-21) the variable is inserted inside a script tag
without further encoding:

```php
<script type="text/javascript">
    if( typeof EM == 'object'){
        if( typeof EM.google_map_id_styles != 'object' ) EM.google_map_id_styles = [];
        EM.google_map_id_styles['<?php echo $args['random_id']; ?>'] = <?php echo $map_json_style; ?>;
    }
</script>
```

This allows the injection of a XSS payload.

[1]: https://codex.wordpress.org/Shortcode_API
[2]: https://codex.wordpress.org/Shortcode_API#HTML

## Proof of Concept ##

To exploit this vulnerability an attacker needs to create or edit a post
and insert one of the shortcodes mentioned above.
In this example we use the `locations_map` shortcode and set the attribute
`map_style` to the base64 encoded value of `{"a":"test\"</script><script>alert(1)</script>"}`.
This will result in the following shortcode:

```text
[locations_map test="" map_style="eyJhIjoidGVzdFwiPC9zY3JpcHQ+PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0PiJ9Cg=="]
```

This shortcode can then be inserted in the post and published by a malicious user.
Anyone visiting the post will be affected by the payload and therefore a victim of the XSS attack.

## Recommended Countermeasures ##

We recommend to properly escape the output by using the encoding functions provided by WordPress,
like the `esc_*`- or `wp_kses_*`-[functions][3].

[3]: https://developer.wordpress.org/themes/theme-security/data-sanitization-escaping/#escaping-securing-output

## Timeline ##

* `2019-09-09` Identified the vulnerability
* `2019-09-10` Contacted vendor
* `2019-09-10` Response by vendor about disclosure contact
* `2019-09-10` Vulnerability disclosed to vendor
* `2019-09-10` Vulnerability verified by vendor, public disclosure coordinated
* `2019-09-20` CVE assigned
* `2019-09-23` Suggested fix verified
* `2019-09-27` Plugin update containing fix was released
* `2019-10-16` Public disclosure

## References ##

* <https://wordpress.org/plugins/events-manager/>
* <https://wordpress.org/plugins/events-manager/#developers>
* <https://wp-events-plugin.com/blog/2019/09/27/events-manager-5-9-6/>

## Credits ##

* Tobias Fink ([SBA Research](https://www.sba-research.org/))
