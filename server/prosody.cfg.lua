admins = { }

modules_enabled = {
    "roster"; "saslauth"; "tls"; "dialback"; "disco";
    "carbons"; "pep"; "private"; "vcard4"; "vcard_legacy";
    "version"; "uptime"; "time"; "ping"; "register"; 
    "admin_adhoc"; "bosh"; "websocket";
}

allow_registration = false
c2s_require_encryption = true  
authentication = "internal_plain"

log = {
    info = "/var/log/prosody/prosody.log";
    error = "/var/log/prosody/prosody.err";
    "*console";
}

VirtualHost "localhost"
    ssl = {
        key = "/etc/prosody/certs/localhost.key";
        certificate = "/etc/prosody/certs/localhost.crt";
    }
