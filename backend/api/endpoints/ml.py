from datetime import datetime
from fastapi import APIRouter, Depends, Query, BackgroundTasks, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from ...database.session import get_session
from ...schemas.packet import MLModelResponse
from ...repositories.threat_repository import MLModelRepository
from ...middleware.auth_middleware import get_current_user
import os
import shutil

router = APIRouter()


@router.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload a custom CSV dataset for ML training."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    os.makedirs("datasets", exist_ok=True)

    # Secure filename
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (".", "_", "-"))
    file_path = os.path.join("datasets", f"uploaded_{safe_filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Dataset uploaded successfully",
        "path": file_path,
        "filename": file.filename
    }



@router.post("/generate-sample")
async def generate_sample_dataset(
    current_user: dict = Depends(get_current_user),
):
    """Generate a sample IDS dataset for testing ML training."""
    import random
    import csv

    os.makedirs("datasets", exist_ok=True)
    path = "datasets/sample_ids_data.csv"

    headers = [
        "duration", "protocol_type", "src_bytes", "dst_bytes",
        "count", "srv_count", "dst_host_count", "dst_host_srv_count",
        "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
        "packet_size", "flow_duration", "fwd_packets", "bwd_packets",
        "fwd_bytes", "bwd_bytes", "flow_bytes_per_sec", "flow_packets_per_sec",
        "avg_packet_size", "fwd_iat_mean",
        "label"
    ]

    attack_types = ["BENIGN", "DDoS", "PortScan", "BruteForce", "BotNet"]

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for _ in range(1000):
            label = random.choice(attack_types)
            is_attack = label != "BENIGN"

            row = [
                random.uniform(0, 60) if not is_attack else random.uniform(0, 5),       # duration
                random.choice(["tcp", "udp", "icmp"]),                                    # protocol_type
                random.randint(0, 5000) if not is_attack else random.randint(500, 50000), # src_bytes
                random.randint(0, 5000) if not is_attack else random.randint(0, 1000),    # dst_bytes
                random.randint(1, 50) if not is_attack else random.randint(50, 500),      # count
                random.randint(1, 30) if not is_attack else random.randint(1, 5),         # srv_count
                random.randint(1, 255),                                                    # dst_host_count
                random.randint(1, 255),                                                    # dst_host_srv_count
                round(random.uniform(0, 1), 4),                                            # dst_host_same_srv_rate
                round(random.uniform(0, 1), 4),                                            # dst_host_diff_srv_rate
                random.randint(40, 1500) if not is_attack else random.randint(40, 100),   # packet_size
                random.uniform(0, 120),                                                    # flow_duration
                random.randint(1, 100) if not is_attack else random.randint(100, 10000),  # fwd_packets
                random.randint(1, 100) if not is_attack else random.randint(0, 10),       # bwd_packets
                random.randint(100, 50000),                                                # fwd_bytes
                random.randint(100, 50000),                                                # bwd_bytes
                round(random.uniform(100, 100000), 2),                                    # flow_bytes_per_sec
                round(random.uniform(1, 1000), 2),                                        # flow_packets_per_sec
                round(random.uniform(40, 1500), 2),                                       # avg_packet_size
                round(random.uniform(0, 5000), 2),                                        # fwd_iat_mean
                label,                                                                     # label
            ]
            writer.writerow(row)

    return {
        "message": "Sample dataset generated successfully",
        "path": path,
        "rows": 1000,
        "instruction": "Now use this path in the Train New Model input field"
    }


def get_pipeline():
    try:
        from ...ml.pipeline import MLPipeline
        return MLPipeline()
    except ImportError as e:
        from fastapi.exceptions import HTTPException
        raise HTTPException(
            status_code=501,
            detail=f"ML dependencies not available in this environment: {e}. Install pandas, numpy, scikit-learn, xgboost."
        )


@router.get("/models", response_model=List[MLModelResponse])
async def list_models(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = MLModelRepository(session)
    models, _ = await repo.get_all(limit=100, order_by="created_at", order_desc=True)
    return [MLModelResponse.model_validate(m) for m in models]


@router.get("/models/active", response_model=Optional[MLModelResponse])
async def get_active_model(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = MLModelRepository(session)
    model = await repo.get_active_model()
    if not model:
        return None
    return MLModelResponse.model_validate(model)


@router.post("/train")
async def train_model(
    dataset_path: str = Query(..., description="Path to training dataset"),
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not os.path.isfile(dataset_path):
        raise HTTPException(status_code=400, detail=f"Dataset file not found: {dataset_path}")

    repo = MLModelRepository(session)

    pipeline = get_pipeline()
    try:
        try:
            df = pipeline.load_dataset(dataset_path)
        except Exception as read_err:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse CSV file. Make sure it is a valid comma-separated text file. Error: {str(read_err)}"
            )
        if df.empty:
            raise HTTPException(status_code=400, detail="The dataset file is empty.")

        if len(df.columns) < 2:
            raise HTTPException(status_code=400, detail="The dataset must contain multiple feature columns and a target label column.")

        df = pipeline.clean_data(df)
        X, y = pipeline.preprocess(df)

        if X.empty or X.shape[1] == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded CSV has no valid numeric features for network threat training. Please upload a valid network capture CSV."
            )

        if len(X) < 10:
            raise HTTPException(
                status_code=400,
                detail=f"The dataset must contain at least 10 samples for training. Current dataset has only {len(X)} usable samples."
            )

        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        results = pipeline.train_models(X_train, y_train)
        if not results:
            raise HTTPException(
                status_code=400,
                detail="Failed to train any ML models on the provided dataset. Ensure your CSV contains valid training data."
            )

        best_name = pipeline.select_best_model(results)
        best_model = results[best_name]["model"]

        metrics = pipeline.evaluate(best_model, X_test, y_test)

        model_path = os.path.join("trained_models", f"model_{best_name}.pkl")
        pipeline.save_model(best_model, model_path)

        ml_model = await repo.create(
            name=f"Model_{best_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            model_type=best_name,
            version="1.0.0",
            file_path=model_path,
            metrics=metrics,
            accuracy=metrics.get("accuracy"),
            precision_macro=metrics.get("precision_macro"),
            recall_macro=metrics.get("recall_macro"),
            f1_macro=metrics.get("f1_macro"),
            roc_auc=metrics.get("roc_auc"),
            confusion_matrix=metrics.get("confusion_matrix"),
            training_dataset=dataset_path,
            training_samples=len(X_train),
            is_trained=True,
            is_active=True,
            feature_columns=pipeline.feature_columns,
        )

        await repo.deactivate_all()
        ml_model.is_active = True
        await session.flush()

        return {
            "message": "Model trained successfully",
            "model_id": str(ml_model.id),
            "model_type": best_name,
            "metrics": metrics,
        }
    except HTTPException:
        raise
    except Exception as e:
        from ...middleware.error_handler import AppException
        raise AppException(message=str(e), status_code=500)


@router.post("/predict")
async def predict_from_flow(
    flow_data: dict,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    pipeline = get_pipeline()
    try:
        from ...feature_engine.extractor import FeatureExtractor
        extractor = FeatureExtractor()
        features = extractor.extract_from_flow(flow_data)

        import pandas as pd
        df = pd.DataFrame([features])
        result = pipeline.predict(df)

        return {
            "predicted_label": result["predicted_label"],
            "confidence": result["confidence"],
            "is_threat": result["is_threat"],
            "features_used": pipeline.feature_columns,
        }
    except Exception as e:
        from ...middleware.error_handler import AppException
        raise AppException(message=str(e), status_code=500)


@router.post("/models/{model_id}/activate")
async def activate_model(
    model_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    pipeline = get_pipeline()
    repo = MLModelRepository(session)
    model = await repo.get(model_id)
    if not model:
        from ...middleware.error_handler import NotFoundException
        raise NotFoundException("Model", model_id)

    await repo.deactivate_all()
    model.is_active = True
    await session.flush()

    try:
        pipeline.load_model(model.file_path)
    except Exception:
        pass

    return {"message": f"Model {model_id} activated"}
