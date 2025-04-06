"""
Mô-đun tạo biểu đồ và hiển thị dữ liệu trực quan
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def create_log_activity_chart(df):
    """
    Tạo biểu đồ hoạt động log theo thời gian
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
    
    Returns:
        plotly.graph_objects.Figure: Biểu đồ hoạt động
    """
    if df.empty or "timestamp" not in df.columns or df["timestamp"].isna().all():
        st.warning("Không có dữ liệu thời gian để hiển thị biểu đồ hoạt động.")
        return None
    
    # Chuyển đổi thành pandas datetime nếu chưa phải
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    
    # Loại bỏ các hàng có timestamp là NaT
    df = df.dropna(subset=["timestamp"])
    
    if df.empty:
        st.warning("Không có dữ liệu thời gian hợp lệ để hiển thị biểu đồ hoạt động.")
        return None
    
    # Thêm cột date để nhóm theo ngày
    df["date"] = df["timestamp"].dt.date
    
    # Đếm số lượng log theo ngày
    daily_counts = df.groupby("date").size().reset_index(name="count")
    
    # Tạo biểu đồ
    fig = px.line(daily_counts, x="date", y="count", 
                 title="Hoạt động log theo thời gian",
                 labels={"date": "Ngày", "count": "Số lượng log"},
                 markers=True)
    
    fig.update_layout(
        xaxis_title="Ngày",
        yaxis_title="Số lượng log",
        hovermode="x unified"
    )
    
    return fig

def create_severity_distribution_chart(df):
    """
    Tạo biểu đồ phân bố mức độ nghiêm trọng của log
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
    
    Returns:
        plotly.graph_objects.Figure: Biểu đồ phân bố mức độ nghiêm trọng
    """
    if df.empty or "severity" not in df.columns:
        st.warning("Không có dữ liệu mức độ nghiêm trọng để hiển thị biểu đồ.")
        return None
    
    # Đếm số lượng log theo mức độ nghiêm trọng
    severity_counts = df["severity"].value_counts().reset_index()
    severity_counts.columns = ["severity", "count"]
    
    # Tạo bảng màu tương ứng với mức độ nghiêm trọng
    color_map = {
        "error": "#d9534f",
        "warning": "#f0ad4e",
        "notice": "#5bc0de",
        "info": "#5cb85c"
    }
    
    colors = [color_map.get(severity, "#777777") for severity in severity_counts["severity"]]
    
    # Tạo biểu đồ
    fig = px.pie(severity_counts, values="count", names="severity",
                title="Phân bố mức độ nghiêm trọng",
                color="severity",
                color_discrete_map=color_map)
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_topic_distribution_chart(df):
    """
    Tạo biểu đồ phân bố chủ đề của log
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
    
    Returns:
        plotly.graph_objects.Figure: Biểu đồ phân bố chủ đề
    """
    if df.empty or "topic" not in df.columns:
        st.warning("Không có dữ liệu chủ đề để hiển thị biểu đồ.")
        return None
    
    # Đếm số lượng log theo chủ đề
    topic_counts = df["topic"].value_counts().reset_index()
    topic_counts.columns = ["topic", "count"]
    
    # Tạo biểu đồ
    fig = px.bar(topic_counts, x="topic", y="count",
                title="Phân bố log theo chủ đề",
                labels={"topic": "Chủ đề", "count": "Số lượng log"},
                color="topic")
    
    fig.update_layout(
        xaxis_title="Chủ đề",
        yaxis_title="Số lượng log",
        hovermode="x unified"
    )
    
    return fig

def create_hourly_activity_chart(df):
    """
    Tạo biểu đồ hoạt động log theo giờ trong ngày
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
    
    Returns:
        plotly.graph_objects.Figure: Biểu đồ hoạt động theo giờ
    """
    if df.empty or "timestamp" not in df.columns or df["timestamp"].isna().all():
        st.warning("Không có dữ liệu thời gian để hiển thị biểu đồ hoạt động theo giờ.")
        return None
    
    # Chuyển đổi thành pandas datetime nếu chưa phải
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    
    # Loại bỏ các hàng có timestamp là NaT
    df = df.dropna(subset=["timestamp"])
    
    if df.empty:
        st.warning("Không có dữ liệu thời gian hợp lệ để hiển thị biểu đồ hoạt động theo giờ.")
        return None
    
    # Thêm cột hour để nhóm theo giờ
    df["hour"] = df["timestamp"].dt.hour
    
    # Đếm số lượng log theo giờ
    hourly_counts = df.groupby("hour").size().reset_index(name="count")
    
    # Tạo danh sách đầy đủ các giờ từ 0-23
    all_hours = pd.DataFrame({"hour": range(24)})
    
    # Merge để đảm bảo có đủ 24 giờ, với giờ không có dữ liệu sẽ có count=0
    hourly_counts = pd.merge(all_hours, hourly_counts, on="hour", how="left").fillna(0)
    
    # Tạo biểu đồ
    fig = px.bar(hourly_counts, x="hour", y="count", 
                title="Hoạt động log theo giờ trong ngày",
                labels={"hour": "Giờ", "count": "Số lượng log"},
                color="count",
                color_continuous_scale="Viridis")
    
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(24)),
            ticktext=[f"{h}:00" for h in range(24)]
        ),
        xaxis_title="Giờ trong ngày",
        yaxis_title="Số lượng log",
        hovermode="x unified"
    )
    
    return fig

def create_top_ip_chart(df, top_n=10):
    """
    Tạo biểu đồ top địa chỉ IP xuất hiện nhiều nhất
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
        top_n (int, optional): Số lượng địa chỉ IP hàng đầu để hiển thị
    
    Returns:
        plotly.graph_objects.Figure: Biểu đồ top địa chỉ IP
    """
    if df.empty or "ip_addresses" not in df.columns:
        st.warning("Không có dữ liệu địa chỉ IP để hiển thị biểu đồ.")
        return None
    
    # Tạo danh sách tất cả các địa chỉ IP
    all_ips = []
    for ip_list in df["ip_addresses"]:
        if pd.notna(ip_list) and ip_list:
            all_ips.extend(ip_list.split(", "))
    
    if not all_ips:
        st.warning("Không có địa chỉ IP nào trong dữ liệu log.")
        return None
    
    # Đếm số lượng xuất hiện của mỗi địa chỉ IP
    from collections import Counter
    ip_counter = Counter(all_ips)
    
    # Lấy top N địa chỉ IP xuất hiện nhiều nhất
    top_ips = ip_counter.most_common(top_n)
    
    # Tạo DataFrame từ top IPs
    top_ip_df = pd.DataFrame(top_ips, columns=["ip", "count"])
    
    # Tạo biểu đồ
    fig = px.bar(top_ip_df, x="ip", y="count",
                title=f"Top {top_n} địa chỉ IP xuất hiện nhiều nhất",
                labels={"ip": "Địa chỉ IP", "count": "Số lượng xuất hiện"},
                color="count",
                color_continuous_scale="Reds")
    
    fig.update_layout(
        xaxis_title="Địa chỉ IP",
        yaxis_title="Số lượng xuất hiện",
        hovermode="x unified"
    )
    
    return fig

def create_interface_activity_chart(df):
    """
    Tạo biểu đồ hoạt động trên các interface
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
    
    Returns:
        plotly.graph_objects.Figure: Biểu đồ hoạt động interface
    """
    if df.empty or "interface" not in df.columns:
        st.warning("Không có dữ liệu interface để hiển thị biểu đồ.")
        return None
    
    # Loại bỏ các hàng không có interface
    df_with_interface = df.dropna(subset=["interface"])
    
    if df_with_interface.empty:
        st.warning("Không có dữ liệu interface hợp lệ để hiển thị biểu đồ.")
        return None
    
    # Đếm số lượng log theo interface
    interface_counts = df_with_interface["interface"].value_counts().reset_index()
    interface_counts.columns = ["interface", "count"]
    
    # Tạo biểu đồ
    fig = px.bar(interface_counts, x="interface", y="count",
                title="Hoạt động log theo interface",
                labels={"interface": "Interface", "count": "Số lượng log"},
                color="interface")
    
    fig.update_layout(
        xaxis_title="Interface",
        yaxis_title="Số lượng log",
        hovermode="x unified"
    )
    
    return fig

def create_topic_by_time_heatmap(df):
    """
    Tạo biểu đồ nhiệt thể hiện phân bố chủ đề theo thời gian
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
    
    Returns:
        plotly.graph_objects.Figure: Biểu đồ nhiệt chủ đề theo thời gian
    """
    if df.empty or "timestamp" not in df.columns or "topic" not in df.columns:
        st.warning("Không đủ dữ liệu để hiển thị biểu đồ nhiệt.")
        return None
    
    # Chuyển đổi thành pandas datetime nếu chưa phải
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    
    # Loại bỏ các hàng có timestamp là NaT
    df = df.dropna(subset=["timestamp"])
    
    if df.empty:
        st.warning("Không có dữ liệu thời gian hợp lệ để hiển thị biểu đồ nhiệt.")
        return None
    
    # Thêm cột hour và date để nhóm
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = df["timestamp"].dt.date
    
    # Đếm số lượng log theo ngày, giờ và chủ đề
    heatmap_data = df.groupby(["date", "hour", "topic"]).size().reset_index(name="count")
    
    # Pivot dữ liệu để phù hợp với biểu đồ nhiệt
    pivot_table = heatmap_data.pivot_table(index="date", columns=["hour", "topic"], values="count", fill_value=0)
    
    # Tạo biểu đồ
    fig = go.Figure()
    
    for topic in df["topic"].unique():
        # Lọc dữ liệu cho chủ đề hiện tại
        topic_data = heatmap_data[heatmap_data["topic"] == topic]
        
        # Nếu không có dữ liệu, bỏ qua
        if topic_data.empty:
            continue
        
        # Tạo biểu đồ nhiệt cho chủ đề này
        topic_pivot = topic_data.pivot_table(index="date", columns="hour", values="count", fill_value=0)
        
        # Tối đa hóa đầu vào cho biểu đồ nhiệt
        z_values = topic_pivot.values
        x_values = topic_pivot.columns.tolist()
        y_values = [str(date) for date in topic_pivot.index]
        
        fig.add_trace(go.Heatmap(
            z=z_values,
            x=x_values,
            y=y_values,
            name=topic,
            visible=False,
            colorscale='Viridis',
            showscale=True
        ))
    
    # Đặt chủ đề đầu tiên ở trạng thái hiển thị
    if len(fig.data) > 0:
        fig.data[0].visible = True
    
    # Thêm thanh chọn chủ đề
    buttons = []
    for i, topic in enumerate(df["topic"].unique()):
        visibility = [False] * len(fig.data)
        visibility[i] = True
        buttons.append(
            dict(
                method="update",
                args=[{"visible": visibility}],
                label=topic
            )
        )
    
    fig.update_layout(
        title="Biểu đồ nhiệt phân bố log theo giờ và ngày",
        xaxis_title="Giờ trong ngày",
        yaxis_title="Ngày",
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                active=0,
                x=1.0,
                y=1.15,
                buttons=buttons
            )
        ],
        annotations=[
            dict(
                text="Chọn chủ đề:",
                x=1.0,
                y=1.08,
                xref="paper",
                yref="paper",
                showarrow=False
            )
        ]
    )
    
    return fig