var PROXY_METHOD = 'SOCKS5 ubuntu.urwork.qbtrade.org:1080';
var PROXY_DROPLET_SG = 'SOCKS5 ubuntu.urwork.qbtrade.org:1080';

var RULES = [
  ".flycandy.com",
  ".qbtrade.org",
  ".ipinfo.io",
  ".facebook.com",
  ".facebook.net",
  ".wikipedia.org",
  ".trello.com",
  ".trellocdn.com",
  ".dropbox.com",
  ".github.com",
  ".stackoverflow.com",
  ".fbcdn.net",
  ".tensorflow.org",
  ".googlevideo.com",
  ".ytimg.com",
  ".ggpht.com",
  ".youtube.com",
  ".googleapis.com",
  ".gstatic.com",
  ".googleusercontent.com",
  ".twitter.com",
  ".w3schools.com",
  ".dropbox.com",
  ".poloniex.com",
  ".gmail.com",
  ".twimg.com",
  ".jsfiddle.net",
  ".amazonaws.com",
  ".google-analytics.com",
  ".golang.org",
  ".bithumb.com",
  ".unpkg.com",
  ".bittrex.com",
  ".bitfinex.com",
  ".binance.com",
  ".bter.com",
  ".jubi.com",  // 因为远程登录抓trans的原因
];

var RULES_SG = [
  ".google.com",
  ".google.com.hk",
  ".google.com.sg"
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

  alert("find proxy " + url + " " + host);
  if (rule_filter(isDomain, RULES) === true) {
    return PROXY_METHOD;
  } else if (rule_filter(isDomain, RULES_SG) === true) {
    return PROXY_DROPLET_SG;
  } else {
    return "DIRECT";
  }

}
