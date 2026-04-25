---
title: "WebRTC IP Leak"
type: concept
tags: [web-scraping, webrtc, ip-leak, udp, proxies, browser-automation]
sources:
  - "Network Fundamentals - Pydoll - Async Web Automation Library.md"
created: 2026-04-23
updated: 2026-04-23
---

# WebRTC IP Leak

WebRTC IP leak is the exposure of a browser's real public IP address through the WebRTC API, even when an HTTP or SOCKS4 proxy is correctly configured. It is the most common cause of IP leakage in proxied browser automation.

## Why It Happens

WebRTC (Web Real-Time Communication) is designed for peer-to-peer audio/video between browsers. To establish a direct P2P connection, it must discover the client's real public IP address using STUN servers over UDP.

The problem: **WebRTC uses UDP, and most proxies only handle TCP.** The STUN query goes directly to the network interface, bypassing the browser's proxy configuration. The OS routing table determines the path, not the browser.

```
HTTP traffic → proxy → destination ✓
WebRTC/STUN → bypasses proxy → real IP exposed ✗
```

## The ICE Process

WebRTC uses ICE (Interactive Connectivity Establishment, RFC 8445) to gather connection candidates:

1. **Host candidates**: local LAN IPs (e.g., `192.168.1.100`) — reveals network topology; Chrome 75+ mitigates with mDNS names when no media permissions granted
2. **Server reflexive candidates**: your real public IP as seen by a STUN server — the primary leak
3. **Relay candidates**: TURN server addresses — may still contain real IP in `raddr` field

JavaScript can read these via `RTCPeerConnection.onicecandidate` and send your real IP to a tracking server.

## Minimal Exploit (10 lines of JS)

```javascript
const pc = new RTCPeerConnection({ iceServers: [{urls: 'stun:stun.l.google.com:19302'}] });
pc.createDataChannel('');
pc.createOffer().then(offer => pc.setLocalDescription(offer));
pc.onicecandidate = (event) => {
    if (event.candidate) {
        const ip = event.candidate.candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3})/)?.[1];
        if (ip) fetch(`/track?real_ip=${ip}`);
    }
};
```

Any page can run this silently without user interaction.

## Why HTTP and SOCKS4 Cannot Stop This

- They only proxy TCP connections
- WebRTC STUN operates on UDP
- WebRTC accesses the OS network stack directly, below the browser's proxy settings

Only SOCKS5 (with UDP ASSOCIATE) or a VPN (which tunnels all IP traffic) can intercept WebRTC's UDP traffic.

## Mitigations

| Method | How | Trade-off |
|---|---|---|
| Force proxied routes (recommended) | `--force-webrtc-ip-handling-policy=disable_non_proxied_udp` | Breaks direct P2P; uses TURN relay (higher latency) |
| Disable WebRTC entirely | `--disable-features=WebRTC` | Breaks all WebRTC-dependent sites |
| SOCKS5 with UDP support | `--proxy-server=socks5://...` + require UDP ASSOCIATE | Proxy must actually support UDP relay |
| VPN | OS-level routing | All traffic tunneled; coarsest control |

In Pydoll: `options.webrtc_leak_protection = True` applies the recommended mitigation.

## Related Bypass Vectors

- **QUIC (HTTP/3)**: also runs over UDP; Chrome uses it by default. Disable with `--disable-quic` flag to force HTTP/2 over TCP and ensure all web traffic stays in the proxy.
- **DNS over UDP**: plain DNS queries bypass TCP-only proxies. SOCKS5 with UDP support proxies DNS; alternatively configure DNS-over-HTTPS.

## Testing

Manual: visit `browserleaks.com/webrtc` — if your real IP appears under "Public IP Address", you're leaking.

Automated: check whether detected IPs include anything other than the proxy IP.

**Always test after configuring WebRTC mitigation.** A single leak instantly compromises the entire proxy setup, revealing real location, ISP, and internal network topology.

## Related Pages

- [[concepts/proxy-rotation]] — proxy types and UDP support matrix
- [[concepts/web-fingerprinting]] — WebRTC leak as one vector in the multi-layer detection system
- [[entities/pydoll]] — `webrtc_leak_protection` property and CDP-based mitigations
- [[summaries/pydoll-network-fingerprinting]] — full network fundamentals including ICE/STUN protocol details
