import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# Set random seed for reproducibility
np.random.seed(42)

# ==========================================
# 1. SYNTHETIC DATASET GENERATION
# ==========================================
def generate_v2v_dataset(n_samples=5000):
    """
    Generates synthetic V2V channel & traffic features paired with optimal
    transmission configurations (Data Rate & Broadcast Interval).
    """
    # Features
    vehicle_density = np.random.uniform(5, 100, n_samples)  # SPDUs/sec (proxy for local density)
    average_rss = np.random.uniform(-95, -50, n_samples)     # dBm
    roadway_type = np.random.choice([0, 1], size=n_samples) # 0: Rural, 1: Urban
    sinr = np.random.uniform(-5, 25, n_samples)              # dB

    targets = []
    
    # Labeling logic mimicking dynamic adaptation rules:
    # High density / low SINR -> Lower data rate, longer interval to reduce congestion.
    # Low density / high SINR -> Higher data rate, shorter interval for fresh state updates.
    for i in range(n_samples):
        dens = vehicle_density[i]
        snr = sinr[i]
        
        # Determine Data Rate (6 Mbps vs 9 Mbps)
        rate = "9Mbps" if snr > 10 else "6Mbps"
        
        # Determine Broadcast Interval (500ms, 1000ms, 2000ms, 5000ms)
        if dens > 75 or snr < 0:
            interval = "5000ms"
        elif dens > 50 or snr < 5:
            interval = "2000ms"
        elif dens > 25 or snr < 12:
            interval = "1000ms"
        else:
            interval = "500ms"
            
        targets.append(f"{rate}_{interval}")

    df = pd.DataFrame({
        'vehicle_density': vehicle_density,
        'average_rss': average_rss,
        'roadway_type': roadway_type,
        'sinr': sinr,
        'target_config': targets
    })
    
    return df

# Load Data
df = generate_v2v_dataset(n_samples=5000)
X = df.drop(columns=['target_config'])
y = df['target_config']

# Split Data (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Feature Scaling (Critical for Distance-based models like SVM and k-NN)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==========================================
# 2. MODEL DEFINITION & TRAINING
# ==========================================
models = {
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "SVM": SVC(kernel='rbf', random_state=42),
    "k-NN": KNeighborsClassifier(n_neighbors=5)
}

results = []
confusion_matrices = {}

# ==========================================
# 3. EVALUATION PIPELINE & LATENCY PROFILING
# ==========================================
for name, model in models.items():
    # Select scaled vs unscaled features based on algorithm requirements
    X_tr = X_train_scaled if name in ["SVM", "k-NN"] else X_train
    X_te = X_test_scaled if name in ["SVM", "k-NN"] else X_test
    
    # Train
    model.fit(X_tr, y_train)
    
    # Measure Inference Latency Per Sample
    start_time = time.perf_counter()
    y_pred = model.predict(X_te)
    end_time = time.perf_counter()
    
    total_latency_sec = end_time - start_time
    latency_per_sample_us = (total_latency_sec / len(X_te)) * 1e6  # Convert to microseconds
    
    # Compute Metrics
    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    
    results.append({
        "Model": name,
        "Accuracy": acc,
        "Macro F1-Score": macro_f1,
        "Latency (μs/sample)": latency_per_sample_us
    })
    
    confusion_matrices[name] = confusion_matrix(y_test, y_pred, labels=np.unique(y))

# Display Metrics Table
results_df = pd.DataFrame(results)
print("=== Performance & Latency Evaluation ===")
print(results_df.to_string(index=False))

# ==========================================
# 4. VISUALIZATION
# ==========================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
labels = np.unique(y)

for idx, (name, cm) in enumerate(confusion_matrices.items()):
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                xticklabels=labels, yticklabels=labels)
    axes[idx].set_title(f"{name} Confusion Matrix")
    axes[idx].set_xlabel("Predicted")
    axes[idx].set_ylabel("Actual")
    axes[idx].tick_params(axis='x', rotation=45)

# Apply exact layout specifications
plt.subplots_adjust(
    left=0.125,
    bottom=0.171,
    right=0.97,
    top=0.94,
    wspace=0.3,
    hspace=0.76
)

plt.show()