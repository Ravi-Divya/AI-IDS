import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from backend.ml.pipeline import MLPipeline
from backend.feature_engine.extractor import FeatureExtractor


class TestMLPipeline:
    @pytest.fixture
    def pipeline(self):
        return MLPipeline()

    @pytest.fixture
    def sample_data(self):
        np.random.seed(42)
        n = 200
        data = {
            "duration": np.random.rand(n) * 1000,
            "protocol_type": np.random.randint(0, 3, n),
            "src_bytes": np.random.randint(0, 10000, n),
            "dst_bytes": np.random.randint(0, 5000, n),
            "count": np.random.randint(0, 100, n),
            "srv_count": np.random.randint(0, 50, n),
            "same_srv_rate": np.random.rand(n),
            "diff_srv_rate": np.random.rand(n),
            "dst_host_count": np.random.randint(0, 255, n),
            "dst_host_srv_count": np.random.randint(0, 255, n),
            "label": np.random.randint(0, 2, n),
        }
        return pd.DataFrame(data)

    def test_preprocessing(self, pipeline, sample_data):
        X, y = pipeline.preprocess(sample_data)
        assert X is not None
        assert y is not None
        assert len(X) == len(y)
        assert X.shape[0] == 200

    def test_training(self, pipeline, sample_data):
        X, y = pipeline.preprocess(sample_data)
        results = pipeline.train_models(X, y)
        assert len(results) > 0
        for name, result in results.items():
            assert "accuracy" in result
            assert result["accuracy"] >= 0

    def test_best_model_selection(self, pipeline, sample_data):
        X, y = pipeline.preprocess(sample_data)
        results = pipeline.train_models(X, y)
        best = pipeline.select_best_model(results)
        assert best in results

    def test_save_and_load(self, pipeline, sample_data, tmp_path):
        X, y = pipeline.preprocess(sample_data)
        results = pipeline.train_models(X, y)
        best_name = pipeline.select_best_model(results)
        model = results[best_name]["model"]

        model_path = str(tmp_path / "test_model.pkl")
        pipeline.save_model(model, model_path)

        new_pipeline = MLPipeline()
        new_pipeline.load_model(model_path)
        assert new_pipeline.is_trained
        assert new_pipeline.model is not None

    def test_prediction(self, pipeline, sample_data):
        X, y = pipeline.preprocess(sample_data)
        results = pipeline.train_models(X, y)
        best_name = pipeline.select_best_model(results)
        model = results[best_name]["model"]
        pipeline.model = model
        pipeline.scaler = pipeline.scaler

        test_features = X.iloc[:1]
        result = pipeline.predict(test_features)
        assert "predicted_label" in result
        assert "confidence" in result
        assert "is_threat" in result


class TestFeatureExtractor:
    @pytest.fixture
    def extractor(self):
        return FeatureExtractor()

    def test_extract_features_from_flow(self, extractor):
        flow = {
            "duration": 120.5,
            "protocol": "tcp",
            "src_ip": "192.168.1.1",
            "dst_ip": "10.0.0.1",
            "src_port": 12345,
            "dst_port": 80,
            "packets_forward": 100,
            "packets_backward": 50,
            "bytes_forward": 50000,
            "bytes_backward": 25000,
            "tcp_flags": "SF",
        }
        features = extractor.extract_from_flow(flow)
        assert len(features) > 50
        assert features["duration"] == 120.5
        assert features["src_bytes"] == 50000
        assert features["dst_bytes"] == 25000
        assert features["protocol_type"] == 0

    def test_port_scan_detection(self, extractor):
        flow = {"src_ip": "192.168.1.100", "dst_port": 80}

        now = datetime.now(timezone.utc)
        recent_flows = [
            {"src_ip": "192.168.1.100", "dst_port": p, "start_time": now}
            for p in range(200)
        ]

        result = extractor.detect_port_scan(flow, recent_flows)
        assert result is not None
        assert result["threat_type"] == "Port Scan"
        assert result["confidence"] == 0.95

    def test_no_false_positive_port_scan(self, extractor):
        flow = {"src_ip": "192.168.1.100", "dst_port": 80}

        now = datetime.now(timezone.utc)
        recent_flows = [
            {"src_ip": "192.168.1.100", "dst_port": 80, "start_time": now}
            for _ in range(3)
        ]

        result = extractor.detect_port_scan(flow, recent_flows)
        assert result is None
