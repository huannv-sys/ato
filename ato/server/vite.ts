// Hỗ trợ cho Vite dev server trong môi trường phát triển
import { createServer as createViteServer } from 'vite';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Lấy __dirname trong ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Tạo middleware Vite cho express
 */
export async function createViteDevMiddleware(app: any) {
  try {
    const clientPath = path.resolve(__dirname, '../client');
    
    // Kiểm tra xem thư mục client có tồn tại không
    if (!fs.existsSync(clientPath)) {
      console.warn(`Thư mục client không tồn tại tại đường dẫn ${clientPath}`);
      return null;
    }
    
    // Tạo Vite server
    const vite = await createViteServer({
      root: clientPath,
      server: {
        middlewareMode: true,
        hmr: true,
        watch: {
          usePolling: true,
        },
      },
      appType: 'spa',
    });
    
    // Sử dụng Vite's connecté middleware
    app.use(vite.middlewares);
    
    console.log("Vite dev middleware đã được thiết lập thành công");
    
    // Trả về middleware Vite để tham chiếu nếu cần
    return vite;
  } catch (error) {
    console.error("Lỗi khi thiết lập Vite dev middleware:", error);
    return null;
  }
}

/**
 * Middleware đối với yêu cầu HTML để Vite xử lý
 */
export function createViteFallbackMiddleware(app: any) {
  // Route cho tất cả các yêu cầu không phải API để Vite xử lý
  app.use('*', (req: any, res: any, next: any) => {
    // Bỏ qua các yêu cầu API
    if (req.originalUrl.startsWith('/api/')) {
      return next();
    }
    
    try {
      // Đọc file index.html từ thư mục client
      const clientPath = path.resolve(__dirname, '../client');
      const indexPath = path.join(clientPath, 'index.html');
      
      if (fs.existsSync(indexPath)) {
        const html = fs.readFileSync(indexPath, 'utf-8');
        res.status(200).set({ 'Content-Type': 'text/html' }).end(html);
      } else {
        res.status(404).send('Không tìm thấy file index.html');
      }
    } catch (e) {
      console.error("Lỗi khi phục vụ index.html:", e);
      res.status(500).end('Lỗi máy chủ nội bộ');
    }
  });
}