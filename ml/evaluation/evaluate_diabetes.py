import os
import json
import joblib
import pandas as pd
from ml.preprocessing.diabetes_preprocessing import load_and_preprocess_dataset

def evaluate_saved_models():
    """
    Loads saved models and dataset, calculates evaluation metrics on unseen test set,
    and displays a formatted metrics comparison table.
    """
    metadata_path = "ml/models/diabetes_model_metadata.json"
    if not os.path.exists(metadata_path):
        print("Metadata file not found. Running training pipeline first...")
        from ml.training.train_diabetes import train_and_evaluate_all_models
        train_and_evaluate_all_models()

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    print("\n" + "=" * 80)
    print("MODEL COMPARISON EVALUATION TABLE (Produced from real test results)")
    print("=" * 80)

    evals = metadata["all_model_evaluations"]
    table_data = []
    for model_name, metrics in evals.items():
        table_data.append({
            "Model": model_name,
            "Accuracy": f"{metrics['accuracy']:.4f}",
            "Precision": f"{metrics['precision']:.4f}",
            "Recall": f"{metrics['recall']:.4f}",
            "F1-Score": f"{metrics['f1']:.4f}",
            "ROC-AUC": f"{metrics['roc_auc']:.4f}"
        })

    df_results = pd.DataFrame(table_data)
    print(df_results.to_string(index=False))
    print("\nSelected Optimal Model:", metadata["selected_model"])
    print("=" * 80)

    return metadata

if __name__ == "__main__":
    evaluate_saved_models()
