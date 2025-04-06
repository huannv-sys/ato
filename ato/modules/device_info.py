"""
Mô-đun xử lý thông tin thiết bị MikroTik
"""
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Cấu trúc dữ liệu thiết bị mặc định
DEFAULT_DEVICE = {
    "name": "",
    "ip_address": "",
    "model": "",
    "serial_number": "",
    "firmware_version": "",
    "location": "",
    "description": "",
    "architecture": "",
    "cpu": "",
    "memory": "",
    "last_update": datetime.now().isoformat()
}

def get_device_info_from_vovi(device_id=None, ip_address=None):
    """
    Lấy thông tin thiết bị từ hệ thống Vovi thông qua API
    
    Args:
        device_id (int, optional): ID của thiết bị (nếu có)
        ip_address (str, optional): Địa chỉ IP của thiết bị (nếu có)
    
    Returns:
        dict: Thông tin thiết bị hoặc mẫu mặc định nếu không tìm thấy
    """
    api_url = os.getenv("VOVI_API_URL")
    
    if not api_url:
        return DEFAULT_DEVICE.copy()
    
    if device_id:
        endpoint = f"{api_url}/devices/{device_id}"
    elif ip_address:
        endpoint = f"{api_url}/devices?ip={ip_address}"
    else:
        return DEFAULT_DEVICE.copy()
    
    try:
        response = requests.get(endpoint, timeout=5)
        if response.status_code == 200:
            device_data = response.json()
            
            # Chuyển đổi dữ liệu từ API sang định dạng của ứng dụng
            return {
                "name": device_data.get("name", ""),
                "ip_address": device_data.get("ipAddress", ""),
                "model": device_data.get("model", ""),
                "serial_number": device_data.get("serialNumber", ""),
                "firmware_version": device_data.get("routerOsVersion", ""),
                "location": device_data.get("location", ""),
                "description": device_data.get("description", ""),
                "architecture": device_data.get("architecture", ""),
                "cpu": device_data.get("cpu", ""),
                "memory": device_data.get("memorySize", ""),
                "last_update": device_data.get("lastUpdated", datetime.now().isoformat())
            }
        else:
            return DEFAULT_DEVICE.copy()
    except Exception as e:
        st.error(f"Lỗi khi kết nối đến API Vovi: {str(e)}")
        return DEFAULT_DEVICE.copy()

def sync_with_vovi_system(device_info):
    """
    Đồng bộ thông tin thiết bị với hệ thống Vovi
    
    Args:
        device_info (dict): Thông tin thiết bị cần đồng bộ
    
    Returns:
        bool: True nếu đồng bộ thành công, False nếu thất bại
    """
    api_url = os.getenv("VOVI_API_URL")
    
    if not api_url:
        st.warning("Chưa cấu hình URL API Vovi. Không thể đồng bộ thông tin.")
        return False
    
    endpoint = f"{api_url}/devices"
    
    # Kiểm tra xem thiết bị đã tồn tại trong hệ thống Vovi chưa
    try:
        # Kiểm tra bằng địa chỉ IP
        check_endpoint = f"{endpoint}?ip={device_info['ip_address']}"
        response = requests.get(check_endpoint, timeout=5)
        
        # Nếu thiết bị đã tồn tại, cập nhật thông tin
        if response.status_code == 200 and response.json():
            device_data = response.json()
            device_id = device_data.get("id")
            
            # Cập nhật thiết bị
            update_data = {
                "name": device_info["name"],
                "model": device_info["model"],
                "serialNumber": device_info["serial_number"],
                "routerOsVersion": device_info["firmware_version"],
                "location": device_info["location"],
                "description": device_info["description"],
                "architecture": device_info["architecture"],
                "cpu": device_info["cpu"],
                "memorySize": device_info["memory"]
            }
            
            update_endpoint = f"{endpoint}/{device_id}"
            update_response = requests.put(update_endpoint, json=update_data, timeout=5)
            
            if update_response.status_code in [200, 201, 204]:
                return True
            else:
                st.error(f"Lỗi khi cập nhật thiết bị: {update_response.text}")
                return False
        
        # Nếu thiết bị chưa tồn tại, tạo mới
        else:
            new_device = {
                "name": device_info["name"],
                "ipAddress": device_info["ip_address"],
                "model": device_info["model"],
                "serialNumber": device_info["serial_number"],
                "routerOsVersion": device_info["firmware_version"],
                "location": device_info["location"],
                "description": device_info["description"],
                "architecture": device_info["architecture"],
                "cpu": device_info["cpu"],
                "memorySize": device_info["memory"],
                "type": "routeros",
                "username": "admin",
                "password": "",
                "status": "online"
            }
            
            create_response = requests.post(endpoint, json=new_device, timeout=5)
            
            if create_response.status_code in [200, 201]:
                return True
            else:
                st.error(f"Lỗi khi tạo thiết bị mới: {create_response.text}")
                return False
            
    except Exception as e:
        st.error(f"Lỗi khi đồng bộ với hệ thống Vovi: {str(e)}")
        return False

def analyze_device_type(device_info):
    """
    Phân tích và xác định loại thiết bị MikroTik dựa trên thông tin
    
    Args:
        device_info (dict): Thông tin thiết bị cần phân tích
    
    Returns:
        dict: Thông tin phân tích bao gồm loại thiết bị, khả năng và vai trò
    """
    model = device_info.get("model", "").lower()
    firmware = device_info.get("firmware_version", "").lower()
    architecture = device_info.get("architecture", "").lower()
    
    device_type = "Unknown"
    capabilities = []
    role = "Unknown"
    
    # Phân tích dựa trên tên model
    if "ccr" in model:
        device_type = "Cloud Core Router"
        capabilities.append("High Performance Routing")
        role = "Core Router"
        
        # Phân tích chi tiết hơn dựa trên số model
        if "2004" in model or "2116" in model or "2216" in model:
            capabilities.append("10G+ Ports")
            capabilities.append("Advanced Routing")
        if "1009" in model or "1016" in model or "1036" in model:
            capabilities.append("Multi-core Processing")
    
    elif "crs" in model:
        device_type = "Cloud Router Switch"
        capabilities.append("Layer 3 Switching")
        role = "Distribution Switch"
        
        if "317" in model or "326" in model or "328" in model:
            capabilities.append("PoE Support")
        if "312" in model or "309" in model:
            capabilities.append("Basic Switching")
    
    elif "rb" in model or "hap" in model:
        if "rb4" in model or "rb3" in model or "rb5" in model:
            device_type = "High Performance Router"
            role = "Edge Router"
            
            if "rb4011" in model or "rb5009" in model:
                capabilities.append("Multi-core Processing")
                capabilities.append("10G Port")
        elif "hap" in model:
            device_type = "Home Access Point"
            capabilities.append("Wireless")
            role = "Access Point"
            
            if "ac" in model:
                capabilities.append("AC Wireless")
            if "ac2" in model or "ac3" in model:
                capabilities.append("Dual-band")
    
    elif "wap" in model:
        device_type = "Wireless Access Point"
        capabilities.append("Wireless")
        role = "Access Point"
    
    elif "hex" in model:
        device_type = "Small Office Router"
        capabilities.append("Compact Size")
        role = "Edge Router"
        
        if "s" in model:
            capabilities.append("Layer 3 Switch")
        if "lite" in model:
            capabilities.append("Budget Device")
            
    # Phân tích dựa trên firmware
    if "6.4" in firmware or "6.5" in firmware or "7." in firmware:
        capabilities.append("Latest RouterOS")
        capabilities.append("Container Support")
    
    # Phân tích dựa trên kiến trúc
    if "arm" in architecture:
        capabilities.append("ARM Architecture")
    elif "mips" in architecture:
        capabilities.append("MIPS Architecture")
    elif "powerpc" in architecture:
        capabilities.append("PowerPC Architecture")
    elif "x86" in architecture or "64" in architecture:
        capabilities.append("x86/x64 Architecture")
        
    return {
        "device_type": device_type,
        "capabilities": capabilities,
        "role": role
    }

def render_device_info_form(initial_data=None):
    """
    Hiển thị và xử lý form thông tin thiết bị
    
    Args:
        initial_data (dict, optional): Dữ liệu ban đầu để hiển thị trong form
    
    Returns:
        dict: Thông tin thiết bị sau khi được cập nhật
    """
    if initial_data is None:
        device_info = DEFAULT_DEVICE.copy()
    else:
        device_info = initial_data.copy()
    
    with st.form("device_info_form"):
        st.subheader("Thông tin thiết bị")
        
        col1, col2 = st.columns(2)
        
        with col1:
            device_info["name"] = st.text_input("Tên thiết bị", value=device_info["name"])
            device_info["ip_address"] = st.text_input("Địa chỉ IP", value=device_info["ip_address"])
            device_info["model"] = st.text_input("Model", value=device_info["model"])
            device_info["serial_number"] = st.text_input("Số serial", value=device_info["serial_number"])
            device_info["firmware_version"] = st.text_input("Phiên bản firmware", value=device_info["firmware_version"])
        
        with col2:
            device_info["location"] = st.text_input("Vị trí", value=device_info["location"])
            device_info["description"] = st.text_area("Mô tả", value=device_info["description"])
            device_info["architecture"] = st.text_input("Kiến trúc", value=device_info["architecture"])
            device_info["cpu"] = st.text_input("CPU", value=device_info["cpu"])
            device_info["memory"] = st.text_input("Bộ nhớ RAM", value=device_info["memory"])
        
        submit = st.form_submit_button("Cập nhật thông tin")
        
        if submit:
            device_info["last_update"] = datetime.now().isoformat()
            # Phân tích loại thiết bị
            analysis = analyze_device_type(device_info)
            
            st.success("Đã cập nhật thông tin thiết bị thành công!")
            
            # Hiển thị thông tin phân tích
            st.subheader("Phân tích thiết bị")
            st.write(f"**Loại thiết bị:** {analysis['device_type']}")
            st.write(f"**Vai trò:** {analysis['role']}")
            st.write("**Khả năng:**")
            for capability in analysis['capabilities']:
                st.write(f"- {capability}")
                
            # Hỏi người dùng có muốn đồng bộ với Vovi không
            if st.button("Đồng bộ với hệ thống Vovi"):
                success = sync_with_vovi_system(device_info)
                if success:
                    st.success("Đã đồng bộ thông tin với hệ thống Vovi thành công!")
                else:
                    st.error("Không thể đồng bộ thông tin với hệ thống Vovi.")
    
    return device_info

def load_device_info_from_file(file_path):
    """
    Tải thông tin thiết bị từ file JSON
    
    Args:
        file_path (str): Đường dẫn tới file JSON
    
    Returns:
        dict: Thông tin thiết bị hoặc mẫu mặc định nếu không đọc được file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Không thể đọc file thông tin thiết bị: {str(e)}")
        return DEFAULT_DEVICE.copy()

def save_device_info_to_file(device_info, file_path):
    """
    Lưu thông tin thiết bị vào file JSON
    
    Args:
        device_info (dict): Thông tin thiết bị cần lưu
        file_path (str): Đường dẫn tới file JSON
    
    Returns:
        bool: True nếu lưu thành công, False nếu thất bại
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(device_info, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Không thể lưu thông tin thiết bị: {str(e)}")
        return False