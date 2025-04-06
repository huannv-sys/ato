// Simple server to test if the application is working properly
const express = require('express');
const pg = require('pg');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const { Pool } = pg;

const app = express();
const port = process.env.PORT || 5000;
const host = process.env.HOST || '0.0.0.0';

// Create connection pool
let pool;
if (process.env.DATABASE_URL) {
  pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  });
}

// Set up middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Log requests
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});

// Basic route
app.get('/', (req, res) => {
  res.send('ATO MikroTik Management System Test Server');
});

// Test database connection
app.get('/api/db-test', async (req, res) => {
  if (!pool) {
    return res.status(500).json({ error: 'No database connection available' });
  }
  
  try {
    const result = await pool.query('SELECT NOW()');
    res.json({
      status: 'ok',
      message: 'Database connection successful',
      timestamp: result.rows[0].now
    });
  } catch (error) {
    console.error('Database connection error:', error);
    res.status(500).json({
      status: 'error',
      message: 'Database connection failed',
      error: error.message
    });
  }
});

// Start server
async function testConnection() {
  if (pool) {
    try {
      const client = await pool.connect();
      console.log('Database connection successful');
      client.release();
    } catch (err) {
      console.error('Database connection error:', err);
    }
  } else {
    console.log('No database connection string provided');
  }
}

app.listen(port, host, () => {
  console.log(`Server running at http://${host}:${port}/`);
  testConnection();
});