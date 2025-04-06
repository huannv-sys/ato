"""
Mô-đun cấu hình và quản lý logging cho ứng dụng
"""
import logging
import os
import sys
from datetime import datetime

def setup_logger(log_level=logging.INFO):
    """
    Cấu hình logger cho ứng dụng
    
    Args:
        log_level (int): Mức độ log (logging.INFO, logging.DEBUG, ...)
    
    Returns:
        logging.Logger: Đối tượng logger đã được cấu hình
    """
    # Tạo thư mục logs nếu chưa tồn tại
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Tạo tên file log với timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"mikrotik_analyzer_{timestamp}.log")
    
    # Cấu hình định dạng log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Cấu hình logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Tạo và trả về logger
    logger = logging.getLogger("MikroTikAnalyzer")
    
    # Ghi log khởi động ứng dụng
    logger.info("Khởi động ứng dụng MikroTik Log Analyzer")
    
    return logger

class LogCapture:
    """
    Lớp ghi lại log trực tiếp trong giao diện Streamlit
    """
    def __init__(self, container, max_lines=100):
        """
        Khởi tạo đối tượng LogCapture
        
        Args:
            container: Vùng chứa trong Streamlit để hiển thị log
            max_lines (int): Số dòng log tối đa giữ lại
        """
        self.container = container
        self.max_lines = max_lines
        self.logs = []
        self.level_colors = {
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "orange",
            "ERROR": "red",
            "CRITICAL": "purple"
        }
    
    def log(self, level, message):
        """
        Ghi log vào container
        
        Args:
            level (str): Mức độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message (str): Nội dung log
        """
        # Thêm timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Thêm log mới vào đầu danh sách
        self.logs.insert(0, {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "color": self.level_colors.get(level, "black")
        })
        
        # Giới hạn số dòng log
        if len(self.logs) > self.max_lines:
            self.logs = self.logs[:self.max_lines]
        
        # Cập nhật giao diện
        self._update_display()
    
    def clear(self):
        """Xóa toàn bộ log"""
        self.logs = []
        self._update_display()
    
    def _update_display(self):
        """Cập nhật hiển thị trong container"""
        # Xóa nội dung cũ
        self.container.empty()
        
        # Hiển thị từng dòng log với màu tương ứng
        for log in self.logs:
            self.container.markdown(
                f"<span style='color:{log['color']}'>**{log['timestamp']} - {log['level']}:** {log['message']}</span>", 
                unsafe_allow_html=True
            )
    
    def debug(self, message):
        """Log ở mức DEBUG"""
        self.log("DEBUG", message)
    
    def info(self, message):
        """Log ở mức INFO"""
        self.log("INFO", message)
    
    def warning(self, message):
        """Log ở mức WARNING"""
        self.log("WARNING", message)
    
    def error(self, message):
        """Log ở mức ERROR"""
        self.log("ERROR", message)
    
    def critical(self, message):
        """Log ở mức CRITICAL"""
        self.log("CRITICAL", message)