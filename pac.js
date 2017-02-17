var PROXY_METHOD = 'SOCKS5 ubuntu.urwork.qbtrade.org:1080';

var PROXY_DROPLET_SG = 'SOCKS5 ubuntu.urwork.qbtrade.org:1081';


// A very long list. Hopefully chrome will cache it.

// Bypass top Chinese sites
// Sources:
// (1) Custom list
// (2) https://dl-web.dropbox.com/u/3241202/apps/chn-cdn/dnsmasq.server.conf - ihipop
// (3) @xream's whitelist
// (4) Alexa 500

// Feel free to add or edit custom list
var RULES = [
      ".facebook.com",
      ".fbcdn.net",
      ".googlevideo.com",
      ".ytimg.com",
      ".ggpht.com",
      ".youtube.com",
      ".googleapis.com",
      ".gstatic.com",
      ".googleusercontent.com",
      ".twitter.com"
];

var RULES_SG = [
      ".google.com"
];
/**
 * @return {string}
 */
function FindProxyForURL(url, host) {

    function isDomain(domain) {
        var host_length, domain_length;
        return ((domain[0] === '.') ? (host === domain.slice(1) || ((host_length = host.length) >= (domain_length = domain.length) && host.slice(host_length - domain_length) === domain)) : (host === domain));
    }

    function rule_filter(callback, r) {
        // IMPORTANT: Respect the order of RULES.
        for (var j = 0; j < r.length; j++) {
            var rule = r[j];
              if (callback(rule) === true) {
                  return true;
              }
        }
        return false;
    }
    alert("find proxy "+ url + " " + host);
    if (rule_filter(isDomain, RULES) === true){
        return PROXY_METHOD;
    } else if (rule_filter(isDomain, RULES_SG) === true){
        return PROXY_DROPLET_SG;
    } else {
        return "DIRECT";
    }

}
