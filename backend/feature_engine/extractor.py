from typing import Dict, List, Optional, Any
from collections import defaultdict
from datetime import datetime, timezone
from ..config.settings import settings


class FeatureExtractor:
    def __init__(self):
        self._buffer: List[dict] = []
        self._max_buffer = settings.FEATURE_CACHE_SIZE

    def extract_from_flow(self, flow: dict) -> Dict[str, Any]:
        duration = flow.get("duration", 0) or 0.001
        packets_total = flow.get("packets_total", 0) or flow.get("packets_forward", 0) + flow.get("packets_backward", 0)
        bytes_total = flow.get("bytes_total", 0) or flow.get("bytes_forward", 0) + flow.get("bytes_backward", 0)
        packets_forward = flow.get("packets_forward", 0)
        packets_backward = flow.get("packets_backward", 0)
        bytes_forward = flow.get("bytes_forward", 0)
        bytes_backward = flow.get("bytes_backward", 0)

        features = {
            "duration": float(duration),
            "protocol_type": self._encode_protocol(flow.get("protocol", "tcp")),
            "service": self._encode_service(flow.get("dst_port", 0)),
            "flag": self._encode_flags(flow.get("tcp_flags", "")),
            "src_bytes": bytes_forward,
            "dst_bytes": bytes_backward,
            "land": 1 if flow.get("src_ip") == flow.get("dst_ip") else 0,
            "wrong_fragment": flow.get("fragment_errors", 0),
            "urgent": flow.get("urgent_data_count", 0),
            "hot": flow.get("hot_indicators", 0),
            "num_failed_logins": flow.get("failed_logins", 0),
            "logged_in": 1 if flow.get("logged_in", False) else 0,
            "num_compromised": flow.get("compromised_count", 0),
            "root_shell": 1 if flow.get("root_access", False) else 0,
            "su_attempted": flow.get("su_attempts", 0),
            "num_root": flow.get("root_count", 0),
            "num_file_creations": flow.get("file_creations", 0),
            "num_shells": flow.get("shell_count", 0),
            "num_access_files": flow.get("access_files", 0),
            "num_outbound_cmds": flow.get("outbound_cmds", 0),
            "is_host_login": 1 if flow.get("host_login", False) else 0,
            "is_guest_login": 1 if flow.get("guest_login", False) else 0,
            "count": packets_total,
            "srv_count": flow.get("connection_frequency", 0),
            "serror_rate": flow.get("syn_error_rate", 0),
            "srv_serror_rate": flow.get("srv_syn_error_rate", 0),
            "rerror_rate": flow.get("rej_error_rate", 0),
            "srv_rerror_rate": flow.get("srv_rej_error_rate", 0),
            "same_srv_rate": flow.get("same_service_rate", 0),
            "diff_srv_rate": flow.get("diff_service_rate", 0),
            "srv_diff_host_rate": flow.get("srv_diff_host_rate", 0),
            "dst_host_count": flow.get("dst_host_count", 0),
            "dst_host_srv_count": flow.get("dst_host_srv_count", 0),
            "dst_host_same_srv_rate": flow.get("dst_host_same_srv_rate", 0),
            "dst_host_diff_srv_rate": flow.get("dst_host_diff_srv_rate", 0),
            "dst_host_same_src_port_rate": flow.get("dst_host_same_src_port_rate", 0),
            "dst_host_srv_diff_host_rate": flow.get("dst_host_srv_diff_host_rate", 0),
            "dst_host_serror_rate": flow.get("dst_host_serror_rate", 0),
            "dst_host_srv_serror_rate": flow.get("dst_host_srv_serror_rate", 0),
            "dst_host_rerror_rate": flow.get("dst_host_rerror_rate", 0),
            "dst_host_srv_rerror_rate": flow.get("dst_host_srv_rerror_rate", 0),
            "flow_packets_s": packets_total / duration if duration > 0 else 0,
            "flow_bytes_s": bytes_total / duration if duration > 0 else 0,
            "avg_packet_size": bytes_total / packets_total if packets_total > 0 else 0,
            "packet_size_variance": flow.get("packet_size_variance", 0),
            "avg_ttl": flow.get("avg_ttl", 0),
            "window_size_avg": flow.get("window_size_avg", 0),
            "tcp_syn_count": flow.get("tcp_syn_count", 0),
            "tcp_fin_count": flow.get("tcp_fin_count", 0),
            "tcp_rst_count": flow.get("tcp_rst_count", 0),
            "entropy_avg": flow.get("entropy_avg", 0),
            "burst_rate": flow.get("burst_rate", 0),
            "retransmission_count": flow.get("retransmission_count", 0),
            "unique_dst_ports": flow.get("unique_dst_ports", 0),
            "dns_query_count": flow.get("dns_query_count", 0),
            "http_request_count": flow.get("http_request_count", 0),
            "ssh_attempt_count": flow.get("ssh_attempt_count", 0),
            "ftp_command_count": flow.get("ftp_command_count", 0),
            "idle_time": flow.get("idle_time", 0),
            "active_time": flow.get("active_time", 0),
            "mean_flow_idle": flow.get("mean_flow_idle", 0),
            "max_flow_idle": flow.get("max_flow_idle", 0),
            "round_trip_time_avg": flow.get("round_trip_time_avg", 0),
        }

        return features

    def detect_port_scan(self, flow: dict, recent_flows: List[dict]) -> Optional[Dict[str, Any]]:
        src_ip = flow.get("src_ip")
        if not src_ip:
            return None

        src_flows = [f for f in recent_flows if f.get("src_ip") == src_ip]
        unique_ports = set()
        port_sequence = []
        timestamps = []

        for f in src_flows:
            port = f.get("dst_port", 0)
            if port:
                unique_ports.add(port)
                port_sequence.append(port)
                timestamps.append(f.get("start_time", datetime.now(timezone.utc)))

        if len(unique_ports) < 10:
            return None

        if timestamps and len(timestamps) >= 2:
            time_span = (max(timestamps) - min(timestamps)).total_seconds()
        else:
            time_span = 0

        if len(unique_ports) >= 150 and time_span <= 5:
                return {
                    "threat_type": "Port Scan",
                    "severity": "high",
                    "confidence": 0.95,
                    "source": "port_scan_detector",
                    "unique_ports": len(unique_ports),
                    "time_span_seconds": time_span,
                    "ports_per_second": len(unique_ports) / time_span if time_span > 0 else 0,
                    "description": f"Host {src_ip} attempted connections to {len(unique_ports)} ports within {time_span:.1f} seconds",
                }

        return None

    def _encode_protocol(self, protocol: str) -> int:
        mapping = {"tcp": 0, "udp": 1, "icmp": 2, "arp": 3, "ipv6": 4, "dns": 5, "http": 6, "https": 7, "ssh": 8, "ftp": 9, "smtp": 10}
        return mapping.get(protocol.lower(), 11)

    def _encode_service(self, port: int) -> int:
        if port == 80:
            return 0
        elif port == 443:
            return 1
        elif port == 22:
            return 2
        elif port == 21:
            return 3
        elif port == 25:
            return 4
        elif port == 53:
            return 5
        elif port == 3306:
            return 6
        elif port == 5432:
            return 7
        elif port == 6379:
            return 8
        elif port == 8080:
            return 9
        elif port == 8443:
            return 10
        else:
            return 11

    def _encode_flags(self, flags: str) -> int:
        if not flags:
            return 0
        flag_str = str(flags).upper()
        if "SF" in flag_str:
            return 0
        elif "S0" in flag_str or "SYN" in flag_str:
            return 1
        elif "REJ" in flag_str or "RST" in flag_str:
            return 2
        elif "SH" in flag_str:
            return 3
        elif "RSTR" in flag_str:
            return 4
        elif "S1" in flag_str:
            return 5
        elif "S2" in flag_str:
            return 6
        elif "S3" in flag_str:
            return 7
        else:
            return 8

    def create_dataframe(self, flow: dict) -> Any:
        import pandas as pd
        features = self.extract_from_flow(flow)
        df = pd.DataFrame([features])
        return df

    def get_feature_names(self) -> List[str]:
        return list(self._get_feature_template().keys())

    def _get_feature_template(self) -> Dict[str, Any]:
        return self.extract_from_flow({
            "duration": 0, "protocol": "tcp", "src_ip": "", "dst_ip": "",
            "dst_port": 0, "packets_forward": 0, "packets_backward": 0,
            "bytes_forward": 0, "bytes_backward": 0, "tcp_flags": "",
        })
