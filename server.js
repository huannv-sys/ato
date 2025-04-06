// Simple server to test database connection
const express = require('express');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 5000;
const host = process.env.HOST || '0.0.0.0';

// Create PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

// Test the database connection
async function testConnection() {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT NOW()');
    console.log('Database connection successful:', result.rows[0]);
    client.release();
    return true;
  } catch (err) {
    console.error('Database connection error:', err);
    return false;
  }
}

// Routes
app.get('/', async (req, res) => {
  const dbConnected = await testConnection();
  
  res.send(`
    <html>
      <head>
        <title>ATO - Mikrotik Management System</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
          }
          h1 {
            color: #333;
          }
          .status {
            padding: 10px;
            margin: 20px 0;
            border-radius: 4px;
          }
          .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
          }
          .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
          }
          pre {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            overflow: auto;
          }
        </style>
      </head>
      <body>
        <h1>ATO - Mikrotik Management System</h1>
        
        <h2>Trạng thái hệ thống:</h2>
        <div class="status ${dbConnected ? 'success' : 'error'}">
          <strong>Kết nối cơ sở dữ liệu:</strong> ${dbConnected ? 'Đã kết nối' : 'Lỗi kết nối'}
        </div>
        
        <h2>Biến môi trường:</h2>
        <pre>
DATABASE_URL: ${process.env.DATABASE_URL ? '✅ Đã thiết lập' : '❌ Chưa thiết lập'}
PORT: ${process.env.PORT || '5000 (mặc định)'}
HOST: ${process.env.HOST || '0.0.0.0 (mặc định)'}
        </pre>
        
        <h2>Hướng dẫn:</h2>
        <p>Để bắt đầu phát triển trên dự án ATO:</p>
        <ol>
          <li>Chạy script setup: <code>./clone_and_setup.sh</code></li>
          <li>Di chuyển vào thư mục dự án: <code>cd ato</code></li>
          <li>Khởi động máy chủ phát triển: <code>HOST=0.0.0.0 PORT=5000 npm run dev</code></li>
        </ol>
      </body>
    </html>
  `);
});

// API route to check database connection
app.get('/api/status', async (req, res) => {
  const dbConnected = await testConnection();
  
  res.json({
    status: dbConnected ? 'ok' : 'error',
    database: dbConnected ? 'connected' : 'disconnected',
    environment: {
      database_url_set: !!process.env.DATABASE_URL,
      port: process.env.PORT || 5000,
      host: process.env.HOST || '0.0.0.0'
    },
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(port, host, () => {
  console.log(`Server running at http://${host}:${port}`);
  testConnection();
});