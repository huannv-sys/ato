import http from "http";
import { WebSocketServer } from "ws";
import { db } from "./db.js";
import { sql } from "drizzle-orm";
import { schedulerService } from "./services/index.js";
import { trafficAnalyzer } from "./services/traffic-analyzer/index.js";

/**
 * Đăng ký các API route và thiết lập WebSocket
 */
export async function registerRoutes(app: any): Promise<http.Server> {
  // Tạo HTTP server từ app Express
  const server = http.createServer(app);
  
  // Thiết lập WebSocket
  const wss = new WebSocketServer({ server });
  
  // Xử lý kết nối WebSocket
  wss.on("connection", function(ws: any) {
    console.log("WebSocket client connected");
    
    // Gửi dữ liệu test khi kết nối
    ws.send(JSON.stringify({
      type: "connection",
      data: { message: "Kết nối WebSocket thành công" }
    }));
    
    // Xử lý tin nhắn từ client
    ws.on("message", function(message: any) {
      console.log("Received message:", message.toString());
      try {
        const parsed = JSON.parse(message.toString());
        
        // Phản hồi echo
        ws.send(JSON.stringify({
          type: "echo",
          data: parsed
        }));
      } catch (e) {
        console.error("Error parsing message:", e);
      }
    });
    
    // Xử lý đóng kết nối
    ws.on("close", function() {
      console.log("WebSocket client disconnected");
    });
  });
  
  // API endpoints
  
  // API kiểm tra trạng thái hệ thống
  app.get("/api/status", async function(req: any, res: any) {
    try {
      // Kiểm tra kết nối database
      const result = await db.execute(sql`SELECT NOW()`);
      
      res.json({
        status: "ok",
        version: "1.0.0",
        message: "Hệ thống đang hoạt động bình thường",
        time: result[0]?.now || new Date(),
        database: "connected"
      });
    } catch (error: any) {
      console.error("Error checking status:", error);
      res.status(500).json({
        status: "error",
        message: "Lỗi khi kiểm tra trạng thái hệ thống",
        error: error?.message || String(error)
      });
    }
  });

  // API lấy cấu hình hệ thống
  app.get("/api/config", async function(req: any, res: any) {
    try {
      res.json({
        pollingInterval: 60,
        maxConcurrentDevices: 5,
        allowAutoDiscovery: true,
        timeFormat: "24h"
      });
    } catch (error: any) {
      console.error("Error getting config:", error);
      res.status(500).json({
        status: "error",
        message: "Lỗi khi lấy cấu hình hệ thống", 
        error: error?.message || String(error)
      });
    }
  });

  // API lấy dữ liệu traffic analyzer
  app.get("/api/traffic/top", async function(req: any, res: any) {
    try {
      const limit = parseInt(req.query.limit || "10");
      const topTalkers = trafficAnalyzer.getTopTalkers(limit);
      
      res.json({
        status: "ok",
        data: topTalkers
      });
    } catch (error: any) {
      console.error("Error getting top talkers:", error);
      res.status(500).json({
        status: "error",
        message: "Lỗi khi lấy dữ liệu top talkers",
        error: error?.message || String(error)
      });
    }
  });

  // API lấy trạng thái scheduler
  app.get("/api/scheduler/status", async function(req: any, res: any) {
    try {
      const status = schedulerService.getStatus();
      
      res.json({
        status: "ok",
        data: status
      });
    } catch (error: any) {
      console.error("Error getting scheduler status:", error);
      res.status(500).json({
        status: "error",
        message: "Lỗi khi lấy trạng thái scheduler",
        error: error?.message || String(error)
      });
    }
  });
  
  return server;
}