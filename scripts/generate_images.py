import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs('images', exist_ok=True)

# ============ LOAD DATA ============
df = pd.read_csv('datasets/sample_ids_data.csv')
print(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")

# Binary classification: BENIGN = 0, Attack = 1
df['is_attack'] = (df['label'] != 'BENIGN').astype(int)
print(f"BENIGN: {(df['is_attack']==0).sum()}, Attacks: {(df['is_attack']==1).sum()}")

# ============ PREPROCESS ============
le = LabelEncoder()
df['protocol_encoded'] = le.fit_transform(df['protocol_type'])

feature_cols = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count',
                'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
                'dst_host_diff_srv_rate', 'packet_size', 'flow_duration',
                'fwd_packets', 'bwd_packets', 'fwd_bytes', 'bwd_bytes',
                'flow_bytes_per_sec', 'flow_packets_per_sec', 'avg_packet_size',
                'fwd_iat_mean', 'protocol_encoded']

X = df[feature_cols].fillna(0).replace([np.inf, -np.inf], 0)
y_binary = df['is_attack']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_binary, test_size=0.2, random_state=42, stratify=y_binary)

# ============ TRAIN MODELS ============
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
}

from xgboost import XGBClassifier
models['XGBoost'] = XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')

from sklearn.ensemble import IsolationForest

results_list = []
predictions = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
    predictions[name] = (y_pred, y_prob)

    acc = accuracy_score(y_test, y_pred) * 100
    prec = precision_score(y_test, y_pred, zero_division=0) * 100
    rec = recall_score(y_test, y_pred, zero_division=0) * 100
    f1 = f1_score(y_test, y_pred, zero_division=0) * 100

    results_list.append({'Model': name, 'Accuracy': f'{acc:.2f}%', 'Precision': f'{prec:.2f}%',
                         'Recall': f'{rec:.2f}%', 'F1-Score': f'{f1:.2f}%'})
    print(f"{name}: Acc={acc:.2f}% Prec={prec:.2f}% Rec={rec:.2f}% F1={f1:.2f}%")

# Isolation Forest
if_model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
if_pred = if_model.fit_predict(X_train)
if_pred_test = if_model.predict(X_test)
if_pred_binary = np.where(if_pred_test == -1, 1, 0)

acc_if = accuracy_score(y_test, if_pred_binary) * 100
prec_if = precision_score(y_test, if_pred_binary, zero_division=0) * 100
rec_if = recall_score(y_test, if_pred_binary, zero_division=0) * 100
f1_if = f1_score(y_test, if_pred_binary, zero_division=0) * 100

results_list.append({'Model': 'Isolation Forest', 'Accuracy': f'{acc_if:.2f}%',
                     'Precision': f'{prec_if:.2f}%', 'Recall': f'{rec_if:.2f}%', 'F1-Score': f'{f1_if:.2f}%'})
print(f"Isolation Forest: Acc={acc_if:.2f}% Prec={prec_if:.2f}% Rec={rec_if:.2f}% F1={f1_if:.2f}%")

print("\n" + classification_report(y_test, predictions['Random Forest'][0], target_names=['BENIGN', 'Attack']))

# ============ FIGURE 1: CONFUSION MATRIX (Random Forest) ============
fig, ax = plt.subplots(figsize=(8, 7))
cm = confusion_matrix(y_test, predictions['Random Forest'][0])
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['BENIGN', 'Attack'])
disp.plot(ax=ax, cmap='Blues', values_format='d')
ax.set_title('Confusion Matrix - Random Forest (Binary Classification)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('images/confusion_binary.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: images/confusion_binary.png")

# ============ FIGURE 2: FEATURE IMPORTANCE ============
rf = models['Random Forest']
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1][:12]
names = [feature_cols[i] for i in indices]
vals = [importances[i] for i in indices]

fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(names)))
ax.barh(range(len(names)), vals, color=colors)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names)
ax.set_xlabel('Importance Score', fontsize=12)
ax.set_title('Top 12 Feature Importance - Random Forest', fontsize=13, fontweight='bold')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('images/feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: images/feature_importance.png")

# ============ FIGURE 3: FLOWCHART ============
fig, ax = plt.subplots(figsize=(12, 9))
ax.axis('off')

steps_data = [
    ('1. Load Dataset\n(CSV: 1000 flows)', '#1565C0', '#BBDEFB'),
    ('2. Clean & Preprocess\n(Encode, Scale, Split)', '#2E7D32', '#C8E6C9'),
    ('3. Feature Extraction\n(80+ Features per Flow)', '#E65100', '#FFE0B2'),
    ('4. Train ML Models\n(RF, GB, XGBoost, IF)', '#6A1B9A', '#E1BEE7'),
    ('5. Evaluate & Select\n(Best F1-Score)', '#C62828', '#FFCDD2'),
    ('6. Serialize Model\n(Pickle: .pkl file)', '#00838F', '#B2EBF2'),
    ('7. Real-Time Detection\n(Predict + Confidence)', '#37474F', '#CFD8DC'),
    ('8. Alert & Notify\n(7 Channels)', '#F57F17', '#FFF9C4'),
]

positions = [
    (0.08, 0.78), (0.30, 0.78), (0.52, 0.78), (0.74, 0.78),
    (0.08, 0.48), (0.30, 0.48), (0.52, 0.48), (0.74, 0.48),
]

for (text, edge, fill), (x, y) in zip(steps_data, positions):
    ax.add_patch(FancyBboxPatch((x, y), 0.2, 0.14, boxstyle="round,pad=0.03",
                                     facecolor=fill, edgecolor=edge, linewidth=2))
    ax.text(x + 0.1, y + 0.07, text, ha='center', va='center', fontsize=8.5, fontweight='bold')

arrows = [
    (0.28, 0.85, 0.30, 0.85), (0.50, 0.85, 0.52, 0.85), (0.72, 0.85, 0.74, 0.85),
    (0.18, 0.78, 0.18, 0.62), (0.40, 0.78, 0.40, 0.62), (0.62, 0.78, 0.62, 0.62), (0.84, 0.78, 0.84, 0.62),
    (0.28, 0.48, 0.30, 0.48), (0.50, 0.48, 0.52, 0.48), (0.72, 0.48, 0.74, 0.48),
]

for x1, y1, x2, y2 in arrows:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#555', lw=2))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title('AI-IDS: Complete ML Pipeline Flowchart', fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('images/flowchart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: images/flowchart.png")

# ============ FIGURE 4: ATTACK DISTRIBUTION ============
fig, ax = plt.subplots(figsize=(10, 6))
vc = df['label'].value_counts()
colors = ['#66BB6A', '#42A5F5', '#FFA726', '#EF5350', '#AB47BC']
bars = ax.bar(vc.index, vc.values, color=colors[:len(vc)], edgecolor='gray', linewidth=0.8)
for bar, val in zip(bars, vc.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val),
            ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.set_xlabel('Traffic Type', fontsize=12)
ax.set_ylabel('Number of Samples', fontsize=12)
ax.set_title('Distribution of Traffic Classes (1000 Samples)', fontsize=14, fontweight='bold')
ax.tick_params(axis='x', rotation=30)
plt.tight_layout()
plt.savefig('images/attack_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: images/attack_distribution.png")

# ============ FIGURE 5: MODEL COMPARISON ============
df_res = pd.DataFrame(results_list)
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(df_res))
width = 0.2
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
colors_comp = ['#1E88E5', '#43A047', '#FB8C00', '#8E24AA']

for i, m in enumerate(metrics):
    vals = [float(r[m].replace('%','')) for _, r in df_res.iterrows()]
    bars = ax.bar(x + i*width, vals, width, label=m, color=colors_comp[i])
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                f'{val:.1f}', ha='center', va='bottom', fontsize=7.5)

ax.set_xlabel('Algorithm', fontsize=12)
ax.set_ylabel('Score (%)', fontsize=12)
ax.set_title('Model Performance Comparison (Binary Classification)', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(df_res['Model'])
ax.legend(fontsize=10)
ax.set_ylim(0, 108)
plt.tight_layout()
plt.savefig('images/comparison_graph.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: images/comparison_graph.png")

# ============ FIGURE 6: ARCHITECTURE ============
fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('off')

# Three tiers
tiers = [
    ('PRESENTATION TIER\nReact SPA (TypeScript)', '#1565C0', '#BBDEFB', 0.7),
    ('APPLICATION TIER\nFastAPI (Python)', '#2E7D32', '#C8E6C9', 0.4),
    ('DATA TIER\nPostgreSQL', '#E65100', '#FFE0B2', 0.1),
]

for name, edge, fill, y in tiers:
    ax.add_patch(FancyBboxPatch((0.05, y), 0.9, 0.22, boxstyle="round,pad=0.05",
                                     facecolor=fill, edgecolor=edge, linewidth=2.5))
    ax.text(0.5, y + 0.11, name, ha='center', va='center', fontsize=11, fontweight='bold')

# Frontend components
fe_components = ['Dashboard', 'Packets', 'Threats', 'Alerts', 'ML', 'Settings']
for i, comp in enumerate(fe_components):
    x = 0.1 + i * 0.15
    ax.add_patch(FancyBboxPatch((x, 0.76), 0.12, 0.06, boxstyle="round,pad=0.02",
                                     facecolor='white', edgecolor='#1565C0', linewidth=1.5))
    ax.text(x + 0.06, 0.79, comp, ha='center', va='center', fontsize=7, fontweight='bold')

# Backend components
be_components = ['Auth', 'ML Pipeline', 'Alert Engine', 'Simulation']
for i, comp in enumerate(be_components):
    x = 0.1 + i * 0.22
    ax.add_patch(FancyBboxPatch((x, 0.46), 0.18, 0.06, boxstyle="round,pad=0.02",
                                     facecolor='white', edgecolor='#2E7D32', linewidth=1.5))
    ax.text(x + 0.09, 0.49, comp, ha='center', va='center', fontsize=7, fontweight='bold')

# DB components
db_components = ['packets', 'flows', 'threats', 'alerts', 'users']
for i, comp in enumerate(db_components):
    x = 0.1 + i * 0.17
    ax.add_patch(FancyBboxPatch((x, 0.16), 0.13, 0.05, boxstyle="round,pad=0.02",
                                     facecolor='white', edgecolor='#E65100', linewidth=1.5))
    ax.text(x + 0.065, 0.185, comp, ha='center', va='center', fontsize=6.5)

# Arrows between tiers
ax.annotate('', xy=(0.5, 0.68), xytext=(0.5, 0.62),
            arrowprops=dict(arrowstyle='<->', color='#666', lw=2))
ax.text(0.55, 0.65, 'JWT Auth\nREST API', fontsize=7, color='#666', fontweight='bold')

ax.annotate('', xy=(0.5, 0.38), xytext=(0.5, 0.32),
            arrowprops=dict(arrowstyle='<->', color='#666', lw=2))
ax.text(0.55, 0.35, 'SQLAlchemy\nORM', fontsize=7, color='#666', fontweight='bold')

# Notification channels
ax.text(0.5, 0.93, 'Notification Channels: Discord | Slack | Telegram | Email | Desktop | Firebase | Webhook',
        ha='center', va='center', fontsize=9, fontweight='bold', color='#555',
        bbox=dict(facecolor='#F3E5F5', edgecolor='#9C27B0', boxstyle='round,pad=0.3'))

ax.set_title('AI-IDS: Three-Tier System Architecture', fontsize=16, fontweight='bold', pad=10)
plt.tight_layout()
plt.savefig('images/architecture.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: images/architecture.png")

print("\n=== ALL IMAGES GENERATED SUCCESSFULLY ===")
print("\nFiles in images/ folder:")
for f in sorted(os.listdir('images')):
    size = os.path.getsize(f'images/{f}')
    print(f"  {f} ({size/1024:.1f} KB)")
