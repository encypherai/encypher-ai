import ipaddress
import socket
from urllib.parse import urlparse


def validate_https_public_url(url: str, *, resolve_dns: bool = False) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("untrusted url")

    if parsed.username or parsed.password:
        raise ValueError("untrusted url")

    host = (parsed.hostname or "").lower()
    if not host or host == "localhost":
        raise ValueError("untrusted url")

    if parsed.port not in (None, 443):
        raise ValueError("untrusted url")

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        if not resolve_dns:
            return

        try:
            addrs = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        except OSError as exc:
            raise ValueError("untrusted url") from exc

        for _family, _socktype, _proto, _canon, sockaddr in addrs:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)
            if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
                raise ValueError("untrusted url")
    else:
        if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
            raise ValueError("untrusted url")
