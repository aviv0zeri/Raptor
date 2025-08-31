#!/usr/bin/env ts-node

/**
 * 🔗 SIMPLE WEBHOOK INTERFACE - TypeScript
 * =======================================
 * 
 * Simplified webhook interface for testing the model flow
 */

import * as http from 'http';
import * as url from 'url';

interface ModelOutput {
  timestamp: string;
  signal: 'BUY' | 'HOLD' | 'SELL';
  confidence: number;
  price: number;
  reasoning?: string;
}

class SimpleWebhook {
  private server: http.Server;
  private port: number = 5001;
  private signals: ModelOutput[] = [];

  constructor() {
    this.server = http.createServer((req, res) => {
      this.handleRequest(req, res);
    });
  }

  private handleRequest(req: http.IncomingMessage, res: http.ServerResponse): void {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    const parsedUrl = url.parse(req.url || '', true);
    const path = parsedUrl.pathname;
    
    console.log(`🌐 ${req.method} ${path} - ${new Date().toLocaleTimeString()}`);

    if (req.method === 'POST' && path === '/webhook') {
      this.handleWebhook(req, res);
    } else if (req.method === 'GET' && path === '/api/signals') {
      this.handleGetSignals(req, res);
    } else if (req.method === 'GET' && path === '/health') {
      this.handleHealth(req, res);
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Not Found' }));
    }
  }

  private handleWebhook(req: http.IncomingMessage, res: http.ServerResponse): void {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        console.log('📥 Webhook received:', {
          type: payload.type,
          signal: payload.data.signal,
          confidence: `${(payload.data.confidence * 100).toFixed(1)}%`
        });

        this.signals.push(payload.data);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, message: 'Signal received' }));
      } catch (error) {
        console.error('❌ Webhook error:', error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON' }));
      }
    });
  }

  private handleGetSignals(req: http.IncomingMessage, res: http.ServerResponse): void {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      success: true, 
      data: this.signals.slice(-10), // Last 10 signals
      total: this.signals.length 
    }));
  }

  private handleHealth(req: http.IncomingMessage, res: http.ServerResponse): void {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'healthy', 
      timestamp: new Date().toISOString(),
      totalSignals: this.signals.length
    }));
  }

  async start(): Promise<void> {
    return new Promise((resolve) => {
      this.server.listen(this.port, () => {
        console.log('🔗 Simple Webhook Interface Started!');
        console.log(`🌐 Server running on http://localhost:${this.port}`);
        console.log('📡 Available endpoints:');
        console.log('  POST /webhook - Receive model signals');
        console.log('  GET  /api/signals - Get signals');
        console.log('  GET  /health - Health check');
        console.log('🎯 Ready to receive model signals!');
        resolve();
      });
    });
  }

  stop(): void {
    this.server.close();
    console.log('🛑 Simple Webhook stopped');
  }
}

// 🚀 Main execution
async function main() {
  const webhook = new SimpleWebhook();
  
  process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down...');
    webhook.stop();
    process.exit(0);
  });

  await webhook.start();
}

// Run the main function
main().catch(console.error);
