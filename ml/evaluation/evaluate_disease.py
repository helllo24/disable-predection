import os
import json
import pandas as pd
from ml.preprocessing.disease_preprocessing import load_and_preprocess_disease_dataset

def evaluate_saved_disease_models():
    """
    Loads saved metadata for disease classification models and displays a formatted
    comparison evaluation table produced from real test results.
    """
    metadata_path = "ml/models/disease_model_metadata.json"
    if not os.path.exists(metadata_path):
        print("Disease metadata missing. Training disease models first...")
        from ml.training.train_disease import train_and_evaluate_disease_models
        train_and_evaluate_disease_models()

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    print("\n" + "=" * 80)
    print("MULTI-CLASS DISEASE MODEL COMPARISON TABLE (Produced from real test set)")
    print("=" * 80)

    evals = metadata["all_model_evaluations"]
    table_data = []
    for model_name, metrics in evals.items():
        table_data.append({
            "Model": model_name,
            "Accuracy": f"{metrics['accuracy']:.4f}",
            "Precision": f"{metrics['precision']:.4f}",
            "Recall": f"{metrics['recall']:.4f}",
            "F1-Score": f"{metrics['f1']:.4f}"
        })

    df_results = pd.DataFrame(table_data)
    print(df_results.to_string(index=False))
    print("\nSelected Optimal Disease Model:", metadata["selected_model"])
    print("Supported Unique Disease Classes:", metadata["dataset"]["disease_classes_count"])
    print("Supported Symptom Features:", metadata["dataset"]["symptom_features_count"])
    print("=" * 80)

    return metadata

if __name__ == "__main__":
    evaluate_saved_disease_models()
