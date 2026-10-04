import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

st.set_page_config(
    page_title="Grid Asset Anomaly Detector",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Grid Asset Anomaly Detector & Health Monitor")
st.markdown("AI-powered telemetry analysis and unsupervised anomaly detection for substation transformers and converters.")

# Sidebar Controls
st.sidebar.header("Telemetry & AI Parameters")
n_samples = st.sidebar.slider("Simulation Time Steps (Hours)", 200, 2000, 1000, 100)
contamination_rate = st.sidebar.slider("Expected Anomaly Rate (Contamination)", 0.01, 0.05, 0.02, 0.005)
noise_level = st.sidebar.slider("Sensor Noise Level", 0.1, 1.0, 0.2, 0.1)

if st.sidebar.button("Run Telemetry & AI Diagnosis"):
    with st.spinner("Processing sensor telemetry and running Isolation Forest model..."):
        # Generate synthetic telemetry data using lowercase 'h' for pandas compatibility
        np.random.seed(42)
        time = pd.date_range(start="2026-01-01", periods=n_samples, freq="h")
        load_mw = np.random.normal(45.0, 5.0, n_samples)
        top_oil_temp = 0.6 * load_mw + np.random.normal(25.0, 2.0, n_samples)
        vibration = np.random.normal(1.2, noise_level, n_samples)

        # Inject synthetic anomalies
        anomaly_indices = [int(n_samples * 0.15), int(n_samples * 0.32), int(n_samples * 0.60), int(n_samples * 0.75), int(n_samples * 0.89)]
        for idx in anomaly_indices:
            if idx + 5 < n_samples:
                top_oil_temp[idx:idx+5] += np.random.uniform(20, 35, 5)
                vibration[idx:idx+5] += np.random.uniform(3.0, 5.0, 5)

        df_telemetry = pd.DataFrame({
            'timestamp': time,
            'load_mw': load_mw,
            'top_oil_temp_c': top_oil_temp,
            'vibration_mms': vibration
        })

        # Machine Learning Anomaly Detection
        features = ['load_mw', 'top_oil_temp_c', 'vibration_mms']
        X = df_telemetry[features]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        iso_forest = IsolationForest(contamination=contamination_rate, random_state=42)
        df_telemetry['anomaly_score'] = iso_forest.fit_predict(X_scaled)
        df_telemetry['is_anomaly'] = df_telemetry['anomaly_score'].apply(lambda x: 1 if x == -1 else 0)

        total_anomalies = int(df_telemetry['is_anomaly'].sum())

        # Metrics display
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Telemetry Logs", f"{n_samples:,}")
        col2.metric("Detected Asset Anomalies", f"{total_anomalies}", delta=f"-{total_anomalies} faults", delta_color="inverse")
        col3.metric("Model Status", "Optimal / Active")

        # Plotting
        st.subheader("📊 Transformer Top-Oil Temperature & Anomaly Alerts")
        fig, ax = plt.subplots(figsize=(12, 5))

        normal_ops = df_telemetry[df_telemetry['is_anomaly'] == 0]
        fault_ops = df_telemetry[df_telemetry['is_anomaly'] == 1]

        ax.plot(normal_ops['timestamp'], normal_ops['top_oil_temp_c'], label='Normal Operating Temp (°C)', color='dodgerblue', alpha=0.6, linewidth=1)
        ax.scatter(fault_ops['timestamp'], fault_ops['top_oil_temp_c'], label='Detected Thermal / Mechanical Fault', color='crimson', s=60, zorder=5)

        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Top-Oil Temperature (°C)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        st.subheader("📋 Detected Anomaly Records")
        st.dataframe(df_telemetry[df_telemetry['is_anomaly'] == 1], use_container_width=True)
else:
    st.info("👈 Adjust parameters in the sidebar and click **Run Telemetry & AI Diagnosis** to start monitoring asset health.")
