#!/usr/bin/env sh
# Read-only network facts. Proxy values are never printed. Optional single argument: hostname for one HTTPS probe.
set -eu
printf '%s\n' "date_utc: $(date -u '+%Y-%m-%d %H:%M' 2>/dev/null || printf unknown)"
printf '%s\n' "resolv_conf_nameservers:"
conf="${PREFIX:-/nonexistent}/etc/resolv.conf"
if [ -f "$conf" ]; then awk '/^nameserver/ {print "  " $2}' "$conf"; else printf '%s\n' "  none found"; fi
printf '%s\n' "proxy_vars_set:"
for v in http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy NO_PROXY no_proxy; do
  eval "val=\${$v:-}"
  if [ -n "$val" ]; then printf '  %s\n' "$v"; fi
done
if [ -f "${PREFIX:-/nonexistent}/etc/tls/cert.pem" ]; then printf '%s\n' "ca_bundle: present"; else printf '%s\n' "ca_bundle: not found"; fi
printf '%s\n' "curl: $(command -v curl >/dev/null 2>&1 && printf present || printf absent)"
if [ "$#" -ge 1 ]; then
  host="$1"
  case "$host" in
    ''|*[!A-Za-z0-9.-]*) printf '%s\n' "probe: refused (hostname has unexpected characters)"; exit 2 ;;
  esac
  if command -v curl >/dev/null 2>&1; then
    code=$(curl -sS -m 8 -o /dev/null -w '%{http_code}' "https://$host" 2>&1 || true)
    printf '%s\n' "probe_https_$host: $code"
  fi
fi
exit 0
