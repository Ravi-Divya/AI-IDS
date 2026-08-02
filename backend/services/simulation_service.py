"""
Network Traffic Simulation Engine
Generates realistic network traffic data for the AI-IDS system.
This populates: Dashboard, Live Packets, Network Flows, Threats, Alerts, Analytics.
"""
import random
import uuid
import asyncio
import structlog
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

logger = structlog.get_logger(__name__)

# ─── Realistic Network Data Templates ──────────────────────────────
INTERNAL_IPS = [
    "192.168.1.10", "192.168.1.25", "192.168.1.50", "192.168.1.100",
    "192.168.1.150", "192.168.2.10", "192.168.2.20", "10.0.0.5",
    "10.0.0.15", "10.0.1.100", "10.0.1.200", "172.16.0.10",
]

EXTERNAL_IPS = [
    "203.0.113.50", "198.51.100.23", "185.220.101.45", "45.33.32.156",
    "104.26.10.78", "172.217.14.206", "151.101.1.69", "13.107.42.14",
    "31.13.71.36", "93.184.216.34", "23.185.0.2", "52.96.165.130",
]

ATTACKER_IPS = [
    "185.220.101.1", "45.155.205.233", "194.26.192.64", "89.248.167.131",
    "139.59.44.89", "178.128.23.9", "206.189.85.18", "167.71.13.196",
]

COMMON_PORTS = {
    "HTTP": 80, "HTTPS": 443, "SSH": 22, "DNS": 53,
    "SMTP": 25, "FTP": 21, "MySQL": 3306, "PostgreSQL": 5432,
    "RDP": 3389, "TELNET": 23, "NTP": 123, "SNMP": 161,
}

DNS_QUERIES = [
    "google.com", "github.com", "api.stripe.com", "cdn.cloudflare.com",
    "fonts.googleapis.com", "mail.google.com", "update.microsoft.com",
    "s3.amazonaws.com", "login.microsoftonline.com", "slack.com",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "curl/7.88.1", "python-requests/2.31.0", "PostmanRuntime/7.35.0",
]

HTTP_PATHS = [
    "/api/v1/users", "/api/v1/data", "/login", "/dashboard",
    "/assets/main.js", "/images/logo.png", "/api/health", "/index.html",
]

ATTACK_PROFILES = {
    "DDoS": {
        "severity": "critical",
        "threat_level": 9,
        "description": "Distributed Denial of Service attack detected — high volume traffic from multiple sources targeting port {port}",
        "explanation": "Abnormally high packet rate ({pps} pps) with {packets} packets in {duration}s from {src_ip}. Traffic pattern matches volumetric DDoS signature.",
        "recommendation": "Block source IP {src_ip} at firewall level. Enable rate limiting. Consider CDN-based DDoS protection.",
    },
    "PortScan": {
        "severity": "high",
        "threat_level": 7,
        "description": "Port scanning activity detected from {src_ip} — probing {ports} ports on {dst_ip}",
        "explanation": "Source {src_ip} sent SYN packets to {ports} different ports on {dst_ip} within {duration}s. This is characteristic of reconnaissance activity.",
        "recommendation": "Block {src_ip} at firewall. Audit exposed services. Enable port scan detection rules.",
    },
    "BruteForce": {
        "severity": "high",
        "threat_level": 8,
        "description": "Brute force login attempt detected on {service} service (port {port})",
        "explanation": "{attempts} failed authentication attempts from {src_ip} to {dst_ip}:{port} in {duration}s. Pattern consistent with credential stuffing.",
        "recommendation": "Enable account lockout after 5 failed attempts. Implement 2FA. Block {src_ip}.",
    },
    "BotNet": {
        "severity": "critical",
        "threat_level": 9,
        "description": "Botnet C&C communication pattern detected from {src_ip}",
        "explanation": "Periodic beaconing behavior detected: {src_ip} connecting to known C&C IP {dst_ip} every ~{interval}s with encrypted payloads of consistent size.",
        "recommendation": "Isolate infected host {src_ip}. Run malware scan. Block C&C IP {dst_ip} at DNS and firewall level.",
    },
    "DataExfiltration": {
        "severity": "critical",
        "threat_level": 10,
        "description": "Potential data exfiltration detected — large outbound data transfer from {src_ip}",
        "explanation": "Unusual outbound transfer of {bytes} bytes from internal host {src_ip} to external IP {dst_ip}. Transfer occurred outside business hours via encrypted channel.",
        "recommendation": "Immediately isolate {src_ip}. Audit data access logs. Check for unauthorized file access. Notify security team.",
    },
    "SQLInjection": {
        "severity": "high",
        "threat_level": 8,
        "description": "SQL Injection attempt detected in HTTP request to {dst_ip}:{port}",
        "explanation": "Malicious SQL payload detected in HTTP request from {src_ip}. Pattern: UNION SELECT, OR 1=1, DROP TABLE signatures found in request parameters.",
        "recommendation": "Review and patch web application input validation. Enable WAF rules. Block {src_ip}.",
    },
}

TCP_FLAG_SETS = ["SYN", "SYN,ACK", "ACK", "FIN,ACK", "PSH,ACK", "RST", "RST,ACK"]


class SimulationEngine:
    """Generates realistic network traffic simulation data."""

    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def generate_batch(self, session, count: int = 20, attack_ratio: float = 0.15):
        """Generate a batch of realistic network traffic data."""
        from ..models.packet import Packet, Flow
        from ..models.threat import Threat, Prediction
        from ..models.alert import Alert

        now = datetime.now(timezone.utc)
        packets_created = 0
        flows_created = 0
        threats_created = 0
        alerts_created = 0

        for i in range(count):
            is_attack = random.random() < attack_ratio
            ts = now - timedelta(seconds=random.uniform(0, 300))

            if is_attack:
                attack_type = random.choice(list(ATTACK_PROFILES.keys()))
                src_ip = random.choice(ATTACKER_IPS)
                dst_ip = random.choice(INTERNAL_IPS)
                pkt_data = self._generate_attack_packet(attack_type, src_ip, dst_ip, ts)
                flow_data = self._generate_attack_flow(attack_type, src_ip, dst_ip, ts)
            else:
                src_ip = random.choice(INTERNAL_IPS)
                dst_ip = random.choice(EXTERNAL_IPS)
                pkt_data = self._generate_normal_packet(src_ip, dst_ip, ts)
                flow_data = self._generate_normal_flow(src_ip, dst_ip, ts)

            # Create packet
            packet = Packet(**pkt_data)
            session.add(packet)
            packets_created += 1

            # Create flow (50% chance, to avoid too many flows)
            if random.random() < 0.5:
                flow = Flow(**flow_data)
                session.add(flow)
                await session.flush()
                flows_created += 1

                if is_attack:
                    # Create prediction
                    confidence = round(random.uniform(0.85, 0.99), 4)
                    prediction = Prediction(
                        flow_id=flow.id,
                        predicted_class=attack_type,
                        predicted_label=1,
                        confidence=confidence,
                        confidence_scores={attack_type: confidence, "BENIGN": round(1 - confidence, 4)},
                        features_used=["duration", "src_bytes", "dst_bytes", "count", "srv_count"],
                        prediction_time_ms=round(random.uniform(0.5, 5.0), 2),
                        is_threat=True,
                        is_processed=True,
                    )
                    session.add(prediction)
                    await session.flush()

                    # Create threat
                    profile = ATTACK_PROFILES[attack_type]
                    port = flow_data.get("dst_port", 80)
                    service = next((k for k, v in COMMON_PORTS.items() if v == port), "unknown")
                    fmt = {
                        "src_ip": src_ip, "dst_ip": dst_ip, "port": port,
                        "pps": random.randint(500, 50000),
                        "packets": random.randint(1000, 100000),
                        "duration": random.randint(5, 120),
                        "ports": random.randint(10, 1000),
                        "attempts": random.randint(50, 5000),
                        "service": service,
                        "interval": random.randint(30, 300),
                        "bytes": f"{random.randint(10, 500)}MB",
                    }
                    threat = Threat(
                        threat_type=attack_type,
                        severity=profile["severity"],
                        confidence=confidence,
                        threat_level=profile["threat_level"],
                        src_ip=src_ip,
                        dst_ip=dst_ip,
                        src_port=flow_data.get("src_port"),
                        dst_port=port,
                        protocol=flow_data.get("protocol", "TCP"),
                        description=profile["description"].format(**fmt),
                        explanation=profile["explanation"].format(**fmt),
                        recommendation=profile["recommendation"].format(**fmt),
                        flow_id=flow.id,
                        prediction_id=prediction.id,
                        is_mitigated=random.random() < 0.3,
                    )
                    session.add(threat)
                    await session.flush()
                    threats_created += 1

                    # Create alert
                    alert = Alert(
                        threat_id=threat.id,
                        alert_type="intrusion_detection",
                        title=f"{attack_type} Attack Detected from {src_ip}",
                        message=profile["description"].format(**fmt),
                        severity=profile["severity"],
                        confidence=confidence,
                        threat_type=attack_type,
                        src_ip=src_ip,
                        dst_ip=dst_ip,
                        explanation=profile["explanation"].format(**fmt),
                        recommendation=profile["recommendation"].format(**fmt),
                        is_read=random.random() < 0.4,
                        is_acknowledged=random.random() < 0.2,
                    )
                    session.add(alert)
                    alerts_created += 1

        await session.commit()
        logger.info("Simulation batch generated",
                     packets=packets_created, flows=flows_created,
                     threats=threats_created, alerts=alerts_created)
        return {
            "packets": packets_created,
            "flows": flows_created,
            "threats": threats_created,
            "alerts": alerts_created,
        }

    def _generate_normal_packet(self, src_ip: str, dst_ip: str, ts: datetime) -> dict:
        protocol = random.choice(["TCP", "UDP", "TCP", "TCP"])
        service = random.choice(list(COMMON_PORTS.keys()))
        dst_port = COMMON_PORTS[service]
        src_port = random.randint(49152, 65535)
        size = random.randint(64, 1500)

        data = {
            "timestamp": ts,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "protocol": protocol,
            "src_port": src_port,
            "dst_port": dst_port,
            "packet_size": size,
            "payload_size": max(0, size - 40),
            "ttl": random.choice([64, 128, 255]),
            "window_size": random.choice([8192, 16384, 32768, 65535]),
            "tcp_flags": random.choice(TCP_FLAG_SETS) if protocol == "TCP" else None,
            "ip_version": 4,
            "capture_interface": "eth0",
        }

        if dst_port == 53:
            data["dns_query"] = random.choice(DNS_QUERIES)
        elif dst_port in (80, 443):
            data["http_method"] = random.choice(["GET", "POST", "GET", "GET"])
            data["http_uri"] = random.choice(HTTP_PATHS)
            data["http_host"] = random.choice(DNS_QUERIES)
            data["http_user_agent"] = random.choice(USER_AGENTS)

        return data

    def _generate_attack_packet(self, attack_type: str, src_ip: str, dst_ip: str, ts: datetime) -> dict:
        if attack_type == "DDoS":
            return {
                "timestamp": ts,
                "src_ip": src_ip, "dst_ip": dst_ip,
                "protocol": "TCP", "src_port": random.randint(1024, 65535),
                "dst_port": random.choice([80, 443, 8080]),
                "packet_size": random.randint(40, 100),
                "payload_size": 0,
                "ttl": random.randint(30, 60),
                "window_size": 1024,
                "tcp_flags": "SYN",
                "ip_version": 4,
                "capture_interface": "eth0",
            }
        elif attack_type == "PortScan":
            return {
                "timestamp": ts,
                "src_ip": src_ip, "dst_ip": dst_ip,
                "protocol": "TCP", "src_port": random.randint(49152, 65535),
                "dst_port": random.randint(1, 1024),
                "packet_size": 44,
                "payload_size": 0,
                "ttl": random.choice([64, 128]),
                "window_size": 1024,
                "tcp_flags": "SYN",
                "ip_version": 4,
                "capture_interface": "eth0",
            }
        elif attack_type == "BruteForce":
            port = random.choice([22, 3389, 21])
            return {
                "timestamp": ts,
                "src_ip": src_ip, "dst_ip": dst_ip,
                "protocol": "TCP", "src_port": random.randint(49152, 65535),
                "dst_port": port,
                "packet_size": random.randint(100, 300),
                "payload_size": random.randint(50, 200),
                "ttl": random.choice([64, 128]),
                "window_size": 8192,
                "tcp_flags": "PSH,ACK",
                "ip_version": 4,
                "capture_interface": "eth0",
                "ssh_version": "SSH-2.0-libssh2_1.10.0" if port == 22 else None,
            }
        else:
            return {
                "timestamp": ts,
                "src_ip": src_ip, "dst_ip": dst_ip,
                "protocol": random.choice(["TCP", "UDP"]),
                "src_port": random.randint(1024, 65535),
                "dst_port": random.choice([443, 8443, 4443]),
                "packet_size": random.randint(200, 1400),
                "payload_size": random.randint(100, 1200),
                "ttl": random.randint(40, 64),
                "window_size": random.randint(1024, 8192),
                "tcp_flags": "PSH,ACK",
                "ip_version": 4,
                "capture_interface": "eth0",
            }

    def _generate_normal_flow(self, src_ip: str, dst_ip: str, ts: datetime) -> dict:
        protocol = random.choice(["TCP", "UDP", "TCP", "TCP"])
        service = random.choice(list(COMMON_PORTS.keys()))
        dst_port = COMMON_PORTS[service]
        src_port = random.randint(49152, 65535)
        duration = round(random.uniform(0.1, 120.0), 3)
        fwd_pkts = random.randint(5, 200)
        bwd_pkts = random.randint(3, 150)
        fwd_bytes = fwd_pkts * random.randint(64, 1200)
        bwd_bytes = bwd_pkts * random.randint(64, 1400)
        total_pkts = fwd_pkts + bwd_pkts
        total_bytes = fwd_bytes + bwd_bytes

        return {
            "flow_key": f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-{protocol}-{uuid.uuid4().hex[:8]}",
            "src_ip": src_ip, "dst_ip": dst_ip,
            "src_port": src_port, "dst_port": dst_port,
            "protocol": protocol,
            "start_time": ts,
            "end_time": ts + timedelta(seconds=duration),
            "duration": duration,
            "packets_forward": fwd_pkts,
            "packets_backward": bwd_pkts,
            "bytes_forward": fwd_bytes,
            "bytes_backward": bwd_bytes,
            "avg_packet_size": round(total_bytes / total_pkts, 2),
            "avg_forward_packet_size": round(fwd_bytes / fwd_pkts, 2),
            "avg_backward_packet_size": round(bwd_bytes / bwd_pkts, 2) if bwd_pkts else 0,
            "packets_per_second": round(total_pkts / max(duration, 0.001), 2),
            "flow_bytes_per_second": round(total_bytes / max(duration, 0.001), 2),
            "min_packet_size": 64,
            "max_packet_size": random.randint(800, 1500),
            "std_packet_size": round(random.uniform(50, 400), 2),
            "min_ttl": 64, "max_ttl": 128,
            "avg_ttl": round(random.uniform(64, 128), 1),
            "tcp_syn_count": random.randint(1, 3),
            "tcp_ack_count": random.randint(5, fwd_pkts),
            "tcp_fin_count": random.randint(0, 2),
            "tcp_rst_count": 0,
            "tcp_psh_count": random.randint(1, 10),
            "tcp_urg_count": 0,
            "is_complete": True,
            "is_active": False,
        }

    def _generate_attack_flow(self, attack_type: str, src_ip: str, dst_ip: str, ts: datetime) -> dict:
        base = self._generate_normal_flow(src_ip, dst_ip, ts)
        base["is_active"] = True
        base["is_complete"] = False

        if attack_type == "DDoS":
            base["dst_port"] = random.choice([80, 443])
            base["packets_forward"] = random.randint(5000, 100000)
            base["packets_backward"] = random.randint(0, 50)
            base["bytes_forward"] = base["packets_forward"] * random.randint(40, 100)
            base["bytes_backward"] = base["packets_backward"] * 40
            base["duration"] = round(random.uniform(1, 30), 2)
            base["tcp_syn_count"] = base["packets_forward"]
            base["tcp_ack_count"] = 0
            base["packets_per_second"] = round(base["packets_forward"] / max(base["duration"], 0.001), 2)
        elif attack_type == "PortScan":
            base["unique_dst_ports"] = random.randint(50, 1000)
            base["packets_forward"] = base["unique_dst_ports"]
            base["packets_backward"] = random.randint(0, base["unique_dst_ports"] // 2)
            base["tcp_syn_count"] = base["packets_forward"]
            base["tcp_rst_count"] = random.randint(base["packets_forward"] // 2, base["packets_forward"])
            base["duration"] = round(random.uniform(2, 60), 2)
        elif attack_type == "BruteForce":
            base["dst_port"] = random.choice([22, 3389, 21])
            base["packets_forward"] = random.randint(500, 10000)
            base["packets_backward"] = base["packets_forward"]
            base["ssh_attempt_count"] = base["packets_forward"] if base["dst_port"] == 22 else 0
            base["duration"] = round(random.uniform(10, 300), 2)
        elif attack_type == "BotNet":
            base["dst_port"] = random.choice([443, 8443, 4443])
            base["packets_forward"] = random.randint(10, 50)
            base["bytes_forward"] = base["packets_forward"] * random.randint(100, 300)
            base["connection_frequency"] = round(random.uniform(0.01, 0.1), 4)
        elif attack_type == "DataExfiltration":
            base["dst_port"] = 443
            base["bytes_forward"] = random.randint(10_000_000, 500_000_000)
            base["packets_forward"] = base["bytes_forward"] // 1400
            base["duration"] = round(random.uniform(60, 600), 2)

        total_pkts = base["packets_forward"] + base["packets_backward"]
        total_bytes = base["bytes_forward"] + base["bytes_backward"]
        base["avg_packet_size"] = round(total_bytes / max(total_pkts, 1), 2)
        base["flow_bytes_per_second"] = round(total_bytes / max(base["duration"], 0.001), 2)
        base["packets_per_second"] = round(total_pkts / max(base["duration"], 0.001), 2)

        return base
