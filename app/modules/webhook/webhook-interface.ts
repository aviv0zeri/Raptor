#!/usr/bin/env ts-node

/**
 * 🔗 RAPTOR WEBHOOK INTERFACE - TypeScript
 * ========================================
 * 
 * Modern TypeScript webhook interface that receives model signals
 * and provides clean API endpoints for the frontend.
 * 
 * Features:
 * - Receives model signals from ModelReader
 * - Stores signals in memory and logs
 * - Provides REST API endpoints
 * - Real-time console logging
 * - Clean TypeScript interfaces
 */

import express, { Express, Request, Response } from 'express';
import cors from 'cors';
import { ModelOutput, WebhookPayload } from '../model/modelreader.js';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  timestamp: string;
}

interface ServerStats {
  uptime: number;
  totalSignals: number;
  lastSignal?: ModelOutput;
  status: 'running' | 'idle' | 'error';
}

class WebhookInterface {
  private app: Express;
  private port: number = 5001;
  private signals: ModelOutput[] = [];
  private startTime: Date;
  private maxSignalsInMemory: number = 1000;

  constructor() {
    this.app = express();
    this.startTime = new Date();
    this.setupMiddleware();
    this.setupRoutes();
  }

  /**
   * 🔧 Setup Express middleware
   */
  private setupMiddleware(): void {
    // CORS for frontend access
    this.app.use(cors({
      origin: ['http://localhost:3000', 'http://localhost:5173'],
      credentials: true
    }));

    // JSON parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    // Request logging
    this.app.use((req, res, next) => {
      console.log(`🌐 ${req.method} ${req.path} - ${new Date().toLocaleTimeString()}`);
      next();
    });
  }

  /**
   * 🛣️ Setup API routes
   */
  private setupRoutes(): void {
    
    // 📥 Webhook endpoint - receives model signals
    this.app.post('/webhook', (req: Request, res: Response) => {
      try {
        const payload: WebhookPayload = req.body;
        
        console.log('📥 Webhook received:', {
          type: payload.type,
          signal: payload.data.signal,
          confidence: `${(payload.data.confidence * 100).toFixed(1)}%`
        });

        // Store signal
        this.addSignal(payload.data);
        
        const response: ApiResponse = {
          success: true,
          message: 'Signal received successfully',
          timestamp: new Date().toISOString()
        };
        
        res.json(response);
      } catch (error) {
        console.error('❌ Webhook error:', error);
        
        const response: ApiResponse = {
          success: false,
          message: 'Failed to process webhook',
          timestamp: new Date().toISOString()
        };
        
        res.status(500).json(response);
      }
    });

    // 📊 Get all signals
    this.app.get('/api/signals', (req: Request, res: Response) => {
      const limit = parseInt(req.query.limit as string) || 100;
      const signals = this.signals.slice(-limit);
      
      const response: ApiResponse<ModelOutput[]> = {
        success: true,
        data: signals,
        timestamp: new Date().toISOString()
      };
      
      console.log(`📊 Serving ${signals.length} signals`);
      res.json(response);
    });

    // 🎯 Get latest signal
    this.app.get('/api/signals/latest', (req: Request, res: Response) => {
      const latestSignal = this.signals[this.signals.length - 1];
      
      const response: ApiResponse<ModelOutput | null> = {
        success: true,
        data: latestSignal || null,
        timestamp: new Date().toISOString()
      };
      
      console.log('🎯 Serving latest signal:', latestSignal?.signal || 'none');
      res.json(response);
    });

    // 📈 Get server stats
    this.app.get('/api/status', (req: Request, res: Response) => {
      const stats: ServerStats = {
        uptime: Date.now() - this.startTime.getTime(),
        totalSignals: this.signals.length,
        lastSignal: this.signals[this.signals.length - 1],
        status: 'running'
      };
      
      const response: ApiResponse<ServerStats> = {
        success: true,
        data: stats,
        timestamp: new Date().toISOString()
      };
      
      res.json(response);
    });

    // 🧹 Clear signals (for testing)
    this.app.delete('/api/signals', (req: Request, res: Response) => {
      const count = this.signals.length;
      this.signals = [];
      
      const response: ApiResponse = {
        success: true,
        message: `Cleared ${count} signals`,
        timestamp: new Date().toISOString()
      };
      
      console.log(`🧹 Cleared ${count} signals`);
      res.json(response);
    });

    // 🏠 Health check
    this.app.get('/health', (req: Request, res: Response) => {
      res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        uptime: Date.now() - this.startTime.getTime()
      });
    });

    // 404 handler
    this.app.use('*', (req: Request, res: Response) => {
      const response: ApiResponse = {
        success: false,
        message: `Endpoint ${req.originalUrl} not found`,
        timestamp: new Date().toISOString()
      };
      
      res.status(404).json(response);
    });
  }

  /**
   * 📥 Add signal to memory
   */
  private addSignal(signal: ModelOutput): void {
    this.signals.push(signal);
    
    // Keep only recent signals in memory
    if (this.signals.length > this.maxSignalsInMemory) {
      this.signals = this.signals.slice(-this.maxSignalsInMemory);
    }
    
    console.log(`📊 Total signals in memory: ${this.signals.length}`);
  }

  /**
   * 🚀 Start the webhook server
   */
  async start(): Promise<void> {
    return new Promise((resolve) => {
      this.app.listen(this.port, () => {
        console.log('🔗 Raptor Webhook Interface Started!');
        console.log(`🌐 Server running on http://localhost:${this.port}`);
        console.log('📡 Available endpoints:');
        console.log('  POST /webhook - Receive model signals');
        console.log('  GET  /api/signals - Get all signals');
        console.log('  GET  /api/signals/latest - Get latest signal');
        console.log('  GET  /api/status - Get server status');
        console.log('  GET  /health - Health check');
        console.log('');
        console.log('🎯 Ready to receive model signals!');
        
        resolve();
      });
    });
  }

  /**
   * 🛑 Stop the server
   */
  stop(): void {
    console.log('🛑 Stopping Webhook Interface...');
    process.exit(0);
  }
}

// 🚀 Main execution
async function main() {
  const webhook = new WebhookInterface();
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...');
    webhook.stop();
  });

  process.on('SIGTERM', () => {
    console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
    webhook.stop();
  });

  // Start the webhook interface
  await webhook.start();
}

// Run if this file is executed directly
if (require.main === module) {
  main().catch(console.error);
}

export { WebhookInterface, ApiResponse, ServerStats };
