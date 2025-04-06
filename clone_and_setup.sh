#!/bin/bash

# Tạo thông báo màu
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Đang cài đặt ATO từ GitHub...${NC}"

# Kiểm tra xem thư mục 'ato' đã tồn tại chưa
if [ -d "ato" ]; then
  echo -e "${GREEN}Thư mục 'ato' đã tồn tại. Bỏ qua bước clone.${NC}"
else
  # Clone repository
  echo -e "${YELLOW}Đang clone repository...${NC}"
  git clone https://github.com/huannv-sys/ato.git
  
  if [ $? -ne 0 ]; then
    echo -e "${RED}Lỗi khi clone repository. Đang thoát...${NC}"
    exit 1
  fi
fi

# Di chuyển vào thư mục dự án
echo -e "${YELLOW}Di chuyển vào thư mục dự án...${NC}"
cd ato || exit

# Kiểm tra và tạo file .env nếu cần
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}Tạo file .env...${NC}"
  cp backup/.env .env
  # Cập nhật DATABASE_URL với giá trị môi trường
  echo "DATABASE_URL=$DATABASE_URL" >> .env
  echo "PGUSER=$PGUSER" >> .env
  echo "PGHOST=$PGHOST" >> .env
  echo "PGPASSWORD=$PGPASSWORD" >> .env
  echo "PGDATABASE=$PGDATABASE" >> .env
  echo "PGPORT=$PGPORT" >> .env
  echo -e "${GREEN}Đã tạo file .env thành công${NC}"
fi

# Cài đặt dependencies
echo -e "${YELLOW}Đang cài đặt các gói phụ thuộc...${NC}"
npm install

if [ $? -ne 0 ]; then
  echo -e "${RED}Lỗi khi cài đặt các gói phụ thuộc. Đang thoát...${NC}"
  exit 1
fi

# Tạo thư mục shared/zod.ts nếu cần thiết
if [ ! -f "shared/zod.ts" ]; then
  echo -e "${YELLOW}Tạo file shared/zod.ts...${NC}"
  echo "// Tệp này liên kết Zod với Drizzle để sử dụng trong schema
import { z } from 'zod';

export {
  z
};" > shared/zod.ts
  echo -e "${GREEN}Đã tạo shared/zod.ts thành công${NC}"
fi

echo -e "${GREEN}Thiết lập dự án đã hoàn tất!${NC}"
echo -e "${YELLOW}Bạn có thể chạy ứng dụng bằng lệnh:${NC}"
echo -e "${GREEN}cd ato && HOST=0.0.0.0 PORT=5000 npm run dev${NC}"

exit 0