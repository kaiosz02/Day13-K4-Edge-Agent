import streamlit as st
import pandas as pd
import json
import yaml
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Day 13 AI Observability", layout="wide")

@st.cache_data(ttl=30)
def load_data():
    logs = []
    log_path = Path("data/logs.jsonl")
    if log_path.exists():
        with open(log_path, "r") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
    
    if not logs:
        return pd.DataFrame()
        
    # Flatten the payload if it exists (vì các trường như latency_ms có thể nằm trong payload hoặc bên ngoài tùy lúc)
    flattened_logs = []
    for log in logs:
        flat = {k: v for k, v in log.items() if k != 'payload'}
        if 'payload' in log and isinstance(log['payload'], dict):
            for k, v in log['payload'].items():
                flat[k] = v
        flattened_logs.append(flat)
        
    df = pd.DataFrame(flattened_logs)
    if 'ts' in df.columns:
        df['ts'] = pd.to_datetime(df['ts'], errors='coerce')
    return df

@st.cache_data
def load_config():
    with open("config/dashboard.yaml", "r") as f:
        return yaml.safe_load(f)['dashboard']

def draw_threshold(fig, threshold):
    if threshold:
        val = threshold['value']
        op = threshold['operator']
        color = "red" if op == "lte" else "orange"
        text = f"Ngưỡng ({op} {val})"
        fig.add_hline(y=val, line_dash="dash", line_color=color, annotation_text=text)
        
def main():
    config = load_config()
    st.title(config.get('title', 'AI Observability Dashboard'))
    
    # Bảng điều khiển thử nghiệm (Sidebar)
    st.sidebar.header("🚨 Bảng Điều Khiển Sự Cố")
    st.sidebar.markdown("Dùng các nút này để test Checkpoint 3 nhanh gọn.")
    
    import subprocess
    import sys
    
    if st.sidebar.button("🔥 Gây lỗi: Latency (rag_slow)"):
        with st.sidebar.status("Đang kích hoạt... (mất khoảng 10-15s)", expanded=True):
            subprocess.run([sys.executable, "scripts/inject_incident.py", "--scenario", "rag_slow"])
            subprocess.run([sys.executable, "scripts/load_test.py", "--challenge", "--concurrency", "5"])
        st.sidebar.error("Đã châm lửa lỗi RAG chậm (Latency)!")
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("🔥 Gây lỗi: Error (tool_fail)"):
        with st.sidebar.status("Đang kích hoạt... (mất khoảng 5s)", expanded=True):
            subprocess.run([sys.executable, "scripts/inject_incident.py", "--scenario", "tool_fail"])
            subprocess.run([sys.executable, "scripts/load_test.py", "--challenge", "--concurrency", "5"])
        st.sidebar.error("Đã châm lửa lỗi Tool Fail (Error Rate)!")
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("🚀 Bơm thêm Traffic (Normal)"):
        with st.sidebar.status("Đang bơm traffic... (mất khoảng 5s)", expanded=True):
            subprocess.run([sys.executable, "scripts/load_test.py"])
        st.sidebar.success("Đã bơm thêm traffic bình thường!")
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("✅ Dập lửa (Khôi phục toàn bộ)"):
        with st.sidebar.status("Đang khôi phục...", expanded=True):
            subprocess.run([sys.executable, "scripts/inject_incident.py", "--scenario", "rag_slow", "--disable"])
            subprocess.run([sys.executable, "scripts/inject_incident.py", "--scenario", "tool_fail", "--disable"])
            subprocess.run([sys.executable, "scripts/inject_incident.py", "--scenario", "cost_spike", "--disable"])
        st.sidebar.success("Incident đã tắt! Bấm 'Bơm Traffic' để thấy biểu đồ bình thường.")
        st.cache_data.clear()
        st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("🗑️ Reset sạch Log (Xóa lịch sử)"):
        import os
        log_path = Path("data/logs.jsonl")
        if log_path.exists():
            os.remove(log_path)
        subprocess.run([sys.executable, "scripts/load_test.py"])
        st.sidebar.success("Đã xóa log cũ và bơm dữ liệu sạch mới!")
        st.cache_data.clear()
        st.rerun()
    
    df = load_data()
    if df.empty:
        st.warning("Chưa có dữ liệu. Hãy bấm nút 'Bơm thêm Traffic' bên cột trái.")
        return
        
    def filter_df(events):
        return df[df['event'].isin(events)] if 'event' in df.columns else df

    panels = config.get('panels', [])
    
    # Render 2 biểu đồ mỗi hàng
    for i in range(0, len(panels), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(panels):
                panel = panels[i + j]
                with cols[j]:
                    st.subheader(panel['title'])
                    
                    pdf = filter_df(panel['events'])
                    if pdf.empty:
                        st.info("Không có dữ liệu cho biểu đồ này.")
                        continue
                        
                    pid = panel['id']
                    thresh = panel.get('threshold')
                    
                    if pid == 'latency':
                        if 'latency_ms' in pdf.columns:
                            pdf = pdf.dropna(subset=['latency_ms'])
                            pdf['minute'] = pdf['ts'].dt.floor('Min')
                            agg = pdf.groupby('minute')['latency_ms'].quantile([0.5, 0.95, 0.99]).unstack()
                            if not agg.empty:
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=agg.index, y=agg[0.5], name='P50', mode='lines+markers'))
                                fig.add_trace(go.Scatter(x=agg.index, y=agg[0.95], name='P95', mode='lines+markers'))
                                fig.add_trace(go.Scatter(x=agg.index, y=agg[0.99], name='P99', mode='lines+markers'))
                                draw_threshold(fig, thresh)
                                fig.update_layout(yaxis_title="ms")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.write("Chưa đủ dữ liệu tính Latency.")
                    
                    elif pid == 'traffic':
                        pdf['minute'] = pdf['ts'].dt.floor('Min')
                        agg = pdf.groupby('minute').size().reset_index(name='count')
                        if not agg.empty:
                            fig = px.bar(agg, x='minute', y='count')
                            draw_threshold(fig, thresh)
                            fig.update_layout(yaxis_title="requests/min")
                            st.plotly_chart(fig, use_container_width=True)
                            
                    elif pid == 'errors':
                        total_reqs = len(df[df['event'] == 'request_received'])
                        total_errs = len(df[df['event'] == 'request_failed'])
                        err_rate = (total_errs / total_reqs * 100) if total_reqs > 0 else 0
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.metric("Tỷ lệ lỗi (Error Rate)", f"{err_rate:.2f}%", 
                                      delta=f"Cảnh báo: Tỷ lệ lỗi đang vượt ngưỡng {thresh['value']}%" if thresh and err_rate > thresh['value'] else "Bình thường",
                                      delta_color="inverse" if err_rate > (thresh['value'] if thresh else 0) else "normal")
                        
                        with col2:
                            fails = pdf[pdf['event'] == 'request_failed']
                            if not fails.empty and 'error_type' in fails.columns:
                                breakdown = fails['error_type'].value_counts().reset_index()
                                breakdown.columns = ['error_type', 'count']
                                fig = px.pie(breakdown, names='error_type', values='count', hole=0.4, title="Phân bổ loại lỗi")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.write("Chưa có lỗi nào được ghi nhận.")
                            
                    elif pid == 'cost':
                        if 'cost_usd' in pdf.columns:
                            pdf = pdf.dropna(subset=['cost_usd'])
                            pdf['minute'] = pdf['ts'].dt.floor('Min')
                            agg = pdf.groupby('minute')['cost_usd'].sum().reset_index()
                            total_cost = pdf['cost_usd'].sum()
                            
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.metric("Tổng Chi Phí", f"${total_cost:.4f}",
                                          delta=f"Vượt SLO ${thresh['value']}" if thresh and total_cost > thresh['value'] else None,
                                          delta_color="inverse")
                            with col2:
                                fig = px.bar(agg, x='minute', y='cost_usd')
                                fig.update_layout(yaxis_title="USD")
                                st.plotly_chart(fig, use_container_width=True)
                                
                    elif pid == 'tokens':
                        if 'tokens_in' in pdf.columns and 'tokens_out' in pdf.columns:
                            pdf = pdf.dropna(subset=['tokens_in', 'tokens_out'])
                            pdf['minute'] = pdf['ts'].dt.floor('Min')
                            agg = pdf.groupby('minute')[['tokens_in', 'tokens_out']].sum().reset_index()
                            fig = go.Figure()
                            fig.add_trace(go.Bar(x=agg['minute'], y=agg['tokens_in'], name='Tokens In'))
                            fig.add_trace(go.Bar(x=agg['minute'], y=agg['tokens_out'], name='Tokens Out'))
                            fig.update_layout(barmode='stack', yaxis_title="Tokens")
                            st.plotly_chart(fig, use_container_width=True)
                            
                    elif pid == 'quality':
                        if 'quality_score' in pdf.columns:
                            pdf = pdf.dropna(subset=['quality_score'])
                            pdf['minute'] = pdf['ts'].dt.floor('Min')
                            agg = pdf.groupby('minute')['quality_score'].mean().reset_index()
                            if not agg.empty:
                                fig = px.line(agg, x='minute', y='quality_score', markers=True)
                                draw_threshold(fig, thresh)
                                fig.update_yaxes(range=[0, 1], title="Điểm")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.write("Chưa đủ dữ liệu điểm chất lượng.")

if __name__ == "__main__":
    main()
