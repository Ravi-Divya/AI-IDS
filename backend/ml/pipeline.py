import pickle
import structlog
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

logger = structlog.get_logger(__name__)


class MLPipeline:
    def __init__(self):
        self.model: Optional[Any] = None
        self.scaler: Any = None
        self.encoder: Any = None
        self.feature_columns: List[str] = []
        self.model_metrics: Dict[str, Any] = {}
        self._models: Dict[str, Any] = {}
        self._is_trained = False

    def load_dataset(self, dataset_path: str) -> Any:
        import pandas as pd
        path = Path(dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        if path.suffix == ".csv":
            df = pd.read_csv(path)
        elif path.suffix == ".parquet":
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported dataset format: {path.suffix}")

        logger.info("Dataset loaded", path=dataset_path, shape=df.shape)
        return df

    def clean_data(self, df: Any) -> Any:
        import numpy as np
        df = df.copy()
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        return df

    def preprocess(self, df: Any, target_column: str = "label") -> Tuple[Any, Any]:
        import numpy as np
        import pandas as pd
        from sklearn.preprocessing import StandardScaler, LabelEncoder

        df = self.clean_data(df)

        if target_column in df.columns:
            y = df[target_column].values
            X = df.drop(columns=[target_column])
        else:
            y = np.zeros(len(df))
            X = df

        categorical_cols = X.select_dtypes(include=["object"]).columns
        for col in categorical_cols:
            if self.encoder is None:
                self.encoder = LabelEncoder()
                X[col] = self.encoder.fit_transform(X[col].astype(str))
            else:
                X[col] = X[col].astype(str)
                le = LabelEncoder()
                le.classes_ = self.encoder.classes_
                X[col] = X[col].map(lambda s: -1 if s not in le.classes_ else s)
                unknown = X[col] == -1
                if unknown.any():
                    X.loc[unknown, col] = 0
                X[col] = X[col].astype(int)

        numeric_cols = X.select_dtypes(include=[np.number]).columns
        X = X[numeric_cols]

        if self.scaler is None:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)

        self.feature_columns = list(X.columns)

        return pd.DataFrame(X_scaled, columns=self.feature_columns), y

    def train_models(self, X_train: Any, y_train: Any) -> Dict[str, Any]:
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        import xgboost as xgb

        models = {
            "random_forest": RandomForestClassifier(
                n_estimators=10, max_depth=5, random_state=42, n_jobs=1
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=10, max_depth=3, learning_rate=0.1, random_state=42
            ),
            "xgboost": xgb.XGBClassifier(
                n_estimators=10, max_depth=3, learning_rate=0.1,
                random_state=42, n_jobs=1, eval_metric="logloss"
            ),
            "isolation_forest": IsolationForest(
                n_estimators=10, contamination=0.1, random_state=42, n_jobs=1
            ),
        }

        results = {}

        for name, model in models.items():
            try:
                logger.info("Training model", model=name)
                if name == "isolation_forest":
                    model.fit(X_train)
                    y_pred = model.predict(X_train)
                    y_pred = np.where(y_pred == -1, 1, 0)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_train)

                accuracy = accuracy_score(y_train, y_pred)
                precision = precision_score(y_train, y_pred, average="macro", zero_division=0)
                recall = recall_score(y_train, y_pred, average="macro", zero_division=0)
                f1 = f1_score(y_train, y_pred, average="macro", zero_division=0)

                results[name] = {
                    "model": model,
                    "accuracy": float(accuracy),
                    "precision": float(precision),
                    "recall": float(recall),
                    "f1_score": float(f1),
                }
                logger.info("Model trained", model=name, accuracy=accuracy)
            except Exception as e:
                logger.error("Model training failed", model=name, error=str(e))

        return results

    def select_best_model(self, results: Dict[str, Any]) -> str:
        best_name = max(results, key=lambda k: results[k]["f1_score"])
        logger.info("Best model selected", model=best_name, metrics=results[best_name])
        return best_name

    def evaluate(self, model: Any, X_test: Any, y_test: Any) -> Dict[str, Any]:
        import numpy as np
        from sklearn.ensemble import IsolationForest
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report

        if isinstance(model, IsolationForest):
            y_pred = model.predict(X_test)
            y_pred = np.where(y_pred == -1, 1, 0)
            y_proba = None
        else:
            y_pred = model.predict(X_test)
            try:
                y_proba = model.predict_proba(X_test)
                if y_proba.shape[1] >= 2:
                    y_proba = y_proba[:, 1]
                else:
                    y_proba = None
            except Exception:
                y_proba = None

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
        recall = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        roc_auc = float(roc_auc_score(y_test, y_proba)) if y_proba is not None and len(np.unique(y_test)) == 2 else None

        metrics = {
            "accuracy": float(accuracy),
            "precision_macro": float(precision),
            "recall_macro": float(recall),
            "f1_macro": float(f1),
            "roc_auc": roc_auc,
            "confusion_matrix": cm,
            "classification_report": report,
        }

        self.model_metrics.update(metrics)
        return metrics

    def save_model(self, model: Any, path: str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"model": model, "scaler": self.scaler, "encoder": self.encoder,
                          "feature_columns": self.feature_columns, "metrics": self.model_metrics}, f)
        logger.info("Model saved", path=str(path))

    def load_model(self, path: str) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")

        with open(path, "rb") as f:
            data = pickle.load(f)

        self.model = data["model"]
        self.scaler = data.get("scaler")
        self.encoder = data.get("encoder")
        self.feature_columns = data.get("feature_columns", [])
        self.model_metrics = data.get("metrics", {})
        self._is_trained = True
        logger.info("Model loaded", path=str(path))

    def predict(self, features: Any) -> Dict[str, Any]:
        from sklearn.ensemble import IsolationForest

        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        if self.scaler:
            missing_cols = [c for c in self.feature_columns if c not in features.columns]
            for col in missing_cols:
                features[col] = 0
            features = features[self.feature_columns]

            try:
                features_scaled = self.scaler.transform(features)
            except Exception:
                features_scaled = features.values
        else:
            features_scaled = features.values

        if isinstance(self.model, IsolationForest):
            y_pred = self.model.predict(features_scaled)
            label = 0 if y_pred[0] == 1 else 1
            confidence = 0.9 if label == 1 else 0.1
        else:
            y_pred = self.model.predict(features_scaled)
            label = int(y_pred[0])
            try:
                proba = self.model.predict_proba(features_scaled)
                if proba.shape[1] >= 2:
                    confidence = float(max(proba[0]))
                else:
                    confidence = 0.5
            except Exception:
                confidence = 0.5

        return {
            "predicted_label": label,
            "confidence": confidence,
            "is_threat": confidence >= settings.CONFIDENCE_THRESHOLD,
        }

    @property
    def is_trained(self) -> bool:
        return self._is_trained or self.model is not None
