const express = require('express');
const { Pool } = require('pg');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 5000;
const host = process.env.HOST || '0.0.0.0';

// Middleware để phân tích request body 
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Kết nối PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

app.get('/api/check', async (req, res) => {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT NOW() as time');
    client.release();
    
    res.json({
      status: 'success',
      message: 'Kết nối đến cơ sở dữ liệu thành công',
      time: result.rows[0].time,
      database_url: process.env.DATABASE_URL ? 'Đã cấu hình' : 'Không tìm thấy'
    });
  } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({
      status: 'error',
      message: 'Lỗi kết nối đến cơ sở dữ liệu',
      error: error.message
    });
  }
});

// Hiển thị thông tin dự án
app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>ATO Project</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
          h1 { color: #333; }
          pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
          .container { margin-top: 20px; }
          button { padding: 10px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
          #result { margin-top: 20px; }
        </style>
      </head>
      <body>
        <h1>ATO Project - Kiểm tra Kết nối</h1>
        <div class="container">
          <p>Kiểm tra kết nối đến cơ sở dữ liệu PostgreSQL:</p>
          <button onclick="checkConnection()">Kiểm tra Kết nối</button>
          <div id="result"></div>
        </div>

        <script>
          async function checkConnection() {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = 'Đang kiểm tra...';
            
            try {
              const response = await fetch('/api/check');
              const data = await response.json();
              
              resultDiv.innerHTML = \`
                <h3>Kết quả:</h3>
                <pre>\${JSON.stringify(data, null, 2)}</pre>
              \`;
            } catch (error) {
              resultDiv.innerHTML = \`
                <h3>Lỗi:</h3>
                <pre>\${error.message}</pre>
              \`;
            }
          }
        </script>
      </body>
    </html>
  `);
});

// Bắt đầu máy chủ
app.listen(port, host, () => {
  console.log(`Máy chủ đang chạy tại http://${host}:${port}`);
});