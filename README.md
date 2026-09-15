# V2V Transmission Scheduling Optimizer (NDSS '24 POC)

A comparative machine learning pipeline designed to dynamically optimize Vehicle-to-Vehicle (V2V) certificate transmission scheduling based on real-time channel conditions and network density.

This proof-of-concept is inspired by concepts from the NDSS 2024 paper *"When Cryptography Needs a Hand: Practical Post-Quantum Authentication for V2V Communications"*.

---

## 📌 Project Overview

Post-Quantum Cryptography (PQC) introduces significantly larger public keys and signatures compared to classical ECDSA. In high-density V2V communication environments, broadcasting large PQC certificates at fixed high rates leads to severe channel congestion and packet collisions. 

This repository implements an adaptive scheduling framework that uses Machine Learning to dynamically select the optimal **Data Rate** and **Broadcast Interval** combinations, reducing broadcast redundancy while satisfying low-latency safety requirements.

---

## 🚗 Target Configurations & Features

### Features (Model Inputs)
1. **`vehicle_density`**: Measured in SPDUs/sec (proxy for local traffic density).
2. **`average_rss`**: Received Signal Strength Indicator (dBm).
3. **`roadway_type`**: Binary categorical encoding (`0`: Rural, `1`: Urban).
4. **`sinr`**: Signal-to-Interference-plus-Noise Ratio (dB).

### Output Classes (8 Target Combinations)
- **Data Rates**: $6\text{ Mbps}, 9\text{ Mbps}$
- **Broadcast Intervals**: $500\text{ ms}, 1000\text{ ms}, 2000\text{ ms}, 5000\text{ ms}$

---

## 🧪 Evaluated Models

1. **Random Forest Classifier** (Primary baseline)
2. **Decision Tree Classifier**
3. **Support Vector Machine (SVM)** (RBF Kernel)
4. **k-Nearest Neighbors (k-NN)**

Models are evaluated on **Accuracy**, **Macro F1-Score**, and **Microsecond Inference Latency per sample** ($\mu\text{s/sample}$), which is critical for real-time On-Board Unit (OBU) deployment constraints.

---

## ⚙️ Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/AppleDinger/V2V-ML-Implementation
cd "V2V ML Implementation"
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the pipeline
```bash
python script.py
```

---

## 📊 Sample Output

Upon execution, the script produces performance metrics alongside inference latency per sample:

```text
=== Performance & Latency Evaluation ===
        Model  Accuracy  Macro F1-Score  Latency (μs/sample)
Decision Tree  0.997000        0.995995             1.432800
Random Forest  0.998000        0.997240            16.273500
          SVM  0.950000        0.942883           171.522100
         k-NN  0.923000        0.918495             6.743900
```

*Note: While Random Forest provides high stability, lightweight decision trees or shallow trees are frequently preferred in V2V environments due to sub-2 microsecond inference latencies.*

---

## 📄 Citation & Reference
- **Paper**: *When Cryptography Needs a Hand: Practical Post-Quantum Authentication for V2V Communications* (NDSS 2024).

---