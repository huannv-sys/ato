"""
Mô-đun xử lý dữ liệu log từ router MikroTik
"""
import re
import pandas as pd
from datetime import datetime
import streamlit as st
import io

# Các mẫu regex thường dùng để phân tích log
REGEX_PATTERNS = {
    "datetime": r"(\w{3}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})",
    "ip_address": r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
    "mac_address": r"([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})",
    "interface": r"interface=(\w+)",
    "login_attempt": r"login attempt|logged in",
    "firewall": r"firewall,info",
    "dhcp": r"dhcp,info",
    "wireless": r"wireless,info",
    "system": r"system,info",
    "connection": r"connection (established|closed|opened)",
    "dropped": r"dropped"
}

def parse_log_line(line):
    """
    Phân tích một dòng log của MikroTik
    
    Args:
        line (str): Dòng log cần phân tích
    
    Returns:
        dict: Thông tin đã phân tích từ dòng log
    """
    # Khởi tạo từ điển chứa thông tin phân tích
    parsed_info = {
        "timestamp": None,
        "topic": None,
        "message": None,
        "ip_addresses": [],
        "mac_addresses": [],
        "interface": None,
        "severity": "info"
    }
    
    # Phân tích thời gian
    datetime_match = re.search(REGEX_PATTERNS["datetime"], line)
    if datetime_match:
        date_str = datetime_match.group(1)
        try:
            parsed_info["timestamp"] = datetime.strptime(date_str, "%b/%d/%Y %H:%M:%S")
        except ValueError:
            pass
    
    # Phân tích địa chỉ IP
    ip_matches = re.findall(REGEX_PATTERNS["ip_address"], line)
    if ip_matches:
        parsed_info["ip_addresses"] = ip_matches
    
    # Phân tích địa chỉ MAC
    mac_matches = re.findall(REGEX_PATTERNS["mac_address"], line)
    if mac_matches:
        parsed_info["mac_addresses"] = mac_matches
    
    # Phân tích interface
    interface_match = re.search(REGEX_PATTERNS["interface"], line)
    if interface_match:
        parsed_info["interface"] = interface_match.group(1)
    
    # Xác định chủ đề
    topics = {
        "firewall": "Firewall",
        "dhcp": "DHCP",
        "wireless": "Wireless",
        "system": "System",
        "login_attempt": "Authentication"
    }
    
    for pattern, topic in topics.items():
        if re.search(REGEX_PATTERNS[pattern], line):
            parsed_info["topic"] = topic
            break
    
    # Nếu không khớp với bất kỳ chủ đề nào, sử dụng chủ đề "Other"
    if parsed_info["topic"] is None:
        parsed_info["topic"] = "Other"
    
    # Xác định mức độ nghiêm trọng
    if "error" in line.lower() or "critical" in line.lower() or "alert" in line.lower():
        parsed_info["severity"] = "error"
    elif "warning" in line.lower():
        parsed_info["severity"] = "warning"
    elif "notice" in line.lower() or "dropped" in line.lower():
        parsed_info["severity"] = "notice"
    
    # Lấy phần message chính
    parts = line.split(":", 1)
    if len(parts) > 1:
        parsed_info["message"] = parts[1].strip()
    else:
        parsed_info["message"] = line
    
    return parsed_info

def process_log_file(file_content):
    """
    Xử lý nội dung file log từ MikroTik
    
    Args:
        file_content (str): Nội dung file log
    
    Returns:
        pandas.DataFrame: DataFrame chứa dữ liệu log đã phân tích
    """
    lines = file_content.splitlines()
    parsed_data = []
    
    # Phân tích từng dòng log
    for line in lines:
        line = line.strip()
        if line:  # Bỏ qua dòng trống
            parsed_info = parse_log_line(line)
            
            # Thêm dòng log gốc cho tham chiếu
            parsed_info["raw_log"] = line
            
            # Chuyển đổi danh sách IP và MAC thành chuỗi cho dễ xử lý trong DataFrame
            parsed_info["ip_addresses"] = ", ".join(parsed_info["ip_addresses"])
            parsed_info["mac_addresses"] = ", ".join(parsed_info["mac_addresses"])
            
            parsed_data.append(parsed_info)
    
    # Tạo DataFrame từ dữ liệu đã phân tích
    df = pd.DataFrame(parsed_data)
    
    # Thêm cột index cho dễ theo dõi
    df = df.reset_index().rename(columns={"index": "log_id"})
    
    return df

def extract_device_info_from_logs(df):
    """
    Trích xuất thông tin về thiết bị từ dữ liệu log
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log đã phân tích
    
    Returns:
        dict: Thông tin về thiết bị
    """
    device_info = {
        "name": "",
        "ip_address": "",
        "model": "",
        "serial_number": "",
        "firmware_version": "",
        "location": "",
        "description": "",
        "architecture": "",
        "cpu": "",
        "memory": ""
    }
    
    # Tìm kiếm thông tin hệ thống trong log
    system_logs = df[df["topic"] == "System"]
    
    # Tìm kiếm thông tin phiên bản RouterOS
    version_logs = system_logs[system_logs["message"].str.contains("routeros", case=False, na=False)]
    if not version_logs.empty:
        for _, row in version_logs.iterrows():
            message = row["message"].lower()
            if "routeros" in message and "version" in message:
                # Tìm kiếm phiên bản RouterOS
                version_match = re.search(r'routeros[^\d]*(\d+\.\d+(\.\d+)?)', message)
                if version_match:
                    device_info["firmware_version"] = version_match.group(1)
    
    # Tìm kiếm thông tin model
    model_logs = system_logs[system_logs["message"].str.contains("model|board|router", case=False, na=False)]
    if not model_logs.empty:
        for _, row in model_logs.iterrows():
            message = row["message"].lower()
            if "model" in message or "board" in message:
                # Tìm kiếm mã model
                model_match = re.search(r'model[^\w]*(rb\w+|ccr\w+|crs\w+|hap\w+)', message, re.IGNORECASE)
                if model_match:
                    device_info["model"] = model_match.group(1)
    
    # Tìm kiếm thông tin IP
    # Lấy các địa chỉ IP xuất hiện nhiều nhất trong log, loại bỏ IP private phổ biến (192.168.1.1, 10.0.0.1, ...)
    all_ips = []
    for ip_list in df["ip_addresses"]:
        if pd.notna(ip_list) and ip_list:
            all_ips.extend(ip_list.split(", "))
    
    # Lọc bỏ các IP private phổ biến
    common_private_ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
    filtered_ips = [ip for ip in all_ips if ip not in common_private_ips]
    
    if filtered_ips:
        # Lấy IP xuất hiện nhiều nhất
        from collections import Counter
        counter = Counter(filtered_ips)
        most_common_ip = counter.most_common(1)[0][0]
        device_info["ip_address"] = most_common_ip
    
    return device_info

def filter_logs_by_criteria(df, filters):
    """
    Lọc dữ liệu log theo các tiêu chí
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
        filters (dict): Các tiêu chí lọc
    
    Returns:
        pandas.DataFrame: DataFrame sau khi lọc
    """
    filtered_df = df.copy()
    
    # Lọc theo thời gian
    if filters.get("start_date") and filters.get("end_date"):
        filtered_df = filtered_df[
            (filtered_df["timestamp"] >= filters["start_date"]) & 
            (filtered_df["timestamp"] <= filters["end_date"])
        ]
    
    # Lọc theo chủ đề
    if filters.get("topic") and filters["topic"] != "All":
        filtered_df = filtered_df[filtered_df["topic"] == filters["topic"]]
    
    # Lọc theo mức độ nghiêm trọng
    if filters.get("severity") and filters["severity"] != "All":
        filtered_df = filtered_df[filtered_df["severity"] == filters["severity"]]
    
    # Lọc theo interface
    if filters.get("interface") and filters["interface"] != "All":
        filtered_df = filtered_df[filtered_df["interface"] == filters["interface"]]
    
    # Lọc theo từ khóa
    if filters.get("keyword"):
        keyword = filters["keyword"].lower()
        filtered_df = filtered_df[
            filtered_df["raw_log"].str.lower().str.contains(keyword, na=False) | 
            filtered_df["message"].str.lower().str.contains(keyword, na=False)
        ]
    
    # Lọc theo địa chỉ IP
    if filters.get("ip_address"):
        ip = filters["ip_address"]
        filtered_df = filtered_df[filtered_df["ip_addresses"].str.contains(ip, na=False)]
    
    # Lọc theo địa chỉ MAC
    if filters.get("mac_address"):
        mac = filters["mac_address"]
        filtered_df = filtered_df[filtered_df["mac_addresses"].str.contains(mac, na=False)]
    
    return filtered_df

def export_to_excel(df, filename="mikrotik_logs.xlsx"):
    """
    Xuất dữ liệu log sang file Excel
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
        filename (str, optional): Tên file Excel
    
    Returns:
        bytes: Dữ liệu file Excel
    """
    # Tạo buffer trong bộ nhớ
    output = io.BytesIO()
    
    # Ghi DataFrame vào buffer dưới dạng Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Logs', index=False)
    
    # Đặt con trỏ về đầu buffer
    output.seek(0)
    
    return output.getvalue()

def analyze_log_statistics(df):
    """
    Phân tích thống kê từ dữ liệu log
    
    Args:
        df (pandas.DataFrame): DataFrame chứa dữ liệu log
    
    Returns:
        dict: Các thống kê từ dữ liệu log
    """
    stats = {}
    
    # Thống kê theo chủ đề
    topic_counts = df["topic"].value_counts().to_dict()
    stats["topic_counts"] = topic_counts
    
    # Thống kê theo mức độ nghiêm trọng
    severity_counts = df["severity"].value_counts().to_dict()
    stats["severity_counts"] = severity_counts
    
    # Thống kê theo thời gian
    if "timestamp" in df.columns and not df["timestamp"].isna().all():
        # Chuyển đổi thành pandas datetime nếu chưa phải
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Thống kê theo ngày
        df["date"] = df["timestamp"].dt.date
        daily_counts = df.groupby("date").size().to_dict()
        stats["daily_counts"] = {str(date): count for date, count in daily_counts.items()}
        
        # Thống kê theo giờ
        df["hour"] = df["timestamp"].dt.hour
        hourly_counts = df.groupby("hour").size().to_dict()
        stats["hourly_counts"] = hourly_counts
    
    # Thống kê các địa chỉ IP xuất hiện nhiều nhất
    all_ips = []
    for ip_list in df["ip_addresses"]:
        if pd.notna(ip_list) and ip_list:
            all_ips.extend(ip_list.split(", "))
    
    from collections import Counter
    ip_counter = Counter(all_ips)
    stats["top_ips"] = dict(ip_counter.most_common(10))
    
    # Thống kê các interface xuất hiện nhiều nhất
    interface_counts = df["interface"].value_counts().to_dict()
    stats["interface_counts"] = interface_counts
    
    return stats