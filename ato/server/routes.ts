import http from "http";
import { WebSocketServer } from "ws";
import { db } from "./db";
import { sql } from "drizzle-orm";

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
  
  return server;
}