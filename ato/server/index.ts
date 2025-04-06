// File này thiết lập và chạy máy chủ

import express from "express";
import dotenv from "dotenv";
import { registerRoutes } from "./routes";
import { schedulerService } from "./services";
import { log, setupVite, serveStatic } from "./vite";

// Load các biến môi trường
dotenv.config();

// Thiết lập Express
const app = express();
app.use(express.json());

// Thiết lập port và host từ biến môi trường
const PORT = process.env.PORT || 5000;
const HOST = process.env.HOST || "localhost";

// Middleware để ghi log các yêu cầu
app.use((req: any, res: any, next: any) => {
  log(`${req.method} ${req.url}`);
  next();
});

// Khởi động máy chủ
async function startServer() {
  try {
    // Khởi tạo scheduler
    schedulerService.initialize();
    
    // Đăng ký các route
    const server = await registerRoutes(app);
    
    // Thiết lập Vite hoặc phục vụ các tệp tĩnh
    const isDev = process.env.NODE_ENV !== "production";
    if (isDev) {
      await setupVite(app, server);
    } else {
      serveStatic(app);
    }
    
    // Khởi động máy chủ
    server.listen(PORT, HOST as any, () => {
      log(`Máy chủ đang chạy tại http://${HOST}:${PORT}`);
    });
    
    // Xử lý lỗi không mong muốn
    app.use((err: any, _req: any, res: any, _next: any) => {
      console.error("Lỗi không mong muốn:", err);
      res.status(500).json({
        status: "error",
        message: "Lỗi máy chủ nội bộ",
        error: process.env.NODE_ENV === "development" ? err.message : undefined
      });
    });
    
  } catch (error) {
    console.error("Lỗi khởi động máy chủ:", error);
    process.exit(1);
  }
}

startServer();