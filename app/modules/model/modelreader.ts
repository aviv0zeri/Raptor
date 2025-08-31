#!/usr/bin/env ts-node

/**
 * 🦖 RAPTOR MODEL READER - TypeScript Interface
 * =============================================
 * 
 * This module initiates the Python model and reads its outputs,
 * converting them to structured data for the webhook interface.
 * 
 * Features:
 * - Initiates Python model via subprocess
 * - Reads model outputs and converts to TypeScript interfaces
 * - Saves results to CSV in logs/
 * - Sends results to webhook interface
 * - Real-time console logging for debugging
 */

import { spawn, ChildProcess } from 'child_process';
import fs from 'fs';
import path from 'path';
import axios from 'axios';

// 🎯 Interfaces
interface ModelOutput {
  timestamp: string;
  signal: 'BUY' | 'HOLD' | 'SELL';
  confidence: number;
  price: number;
  reasoning?: string;
}

interface WebhookPayload {
  type: 'model_signal';
  data: ModelOutput;
  timestamp: string;
}

class ModelReader {
  private pythonProcess: ChildProcess | null = null;
  private isRunning: boolean = false;
  private outputBuffer: string = '';
  private logFilePath: string;
  private webhookUrl: string = 'http://localhost:5001/webhook';

  constructor() {
    this.logFilePath = path.join(process.cwd(), 'logs', 'model_output.csv');
    this.ensureLogDirectory();
    this.initializeCsvFile();
  }

  /**
   * 🚀 Start the model reader
   */
  async start(): Promise<void> {
    console.log('🦖 Starting Raptor Model Reader...');
    console.log('📁 Log file:', this.logFilePath);
    console.log('🔗 Webhook URL:', this.webhookUrl);
    
    try {
      await this.startPythonModel();
      this.isRunning = true;
      console.log('✅ Model Reader started successfully!');
      
      // Keep the process alive
      this.keepAlive();
    } catch (error) {
      console.error('❌ Failed to start Model Reader:', error);
      process.exit(1);
    }
  }

  /**
   * 🐍 Start the Python model process
   */
  private async startPythonModel(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log('🐍 Starting Python model process...');
      
      const pythonScript = path.join(process.cwd(), 'modules', 'model', 'main.py');
      
      this.pythonProcess = spawn('python3', [pythonScript], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.join(process.cwd(), 'modules', 'model')
      });

      this.pythonProcess.stdout?.on('data', (data) => {
        const output = data.toString();
        console.log('🐍 Python Model:', output.trim());
        this.handleModelOutput(output);
      });

      this.pythonProcess.stderr?.on('data', (data) => {
        const error = data.toString();
        console.error('🐍 Python Error:', error.trim());
      });

      this.pythonProcess.on('spawn', () => {
        console.log('✅ Python model process spawned successfully');
        resolve();
      });

      this.pythonProcess.on('error', (error) => {
        console.error('❌ Failed to spawn Python process:', error);
        reject(error);
      });

      this.pythonProcess.on('exit', (code, signal) => {
        console.log(`🐍 Python process exited with code ${code}, signal ${signal}`);
        this.isRunning = false;
      });
    });
  }

  /**
   * 📊 Handle model output from Python
   */
  private handleModelOutput(output: string): void {
    this.outputBuffer += output;
    
    // Look for complete JSON objects in the buffer
    const lines = this.outputBuffer.split('\n');
    this.outputBuffer = lines.pop() || ''; // Keep incomplete line in buffer
    
    for (const line of lines) {
      if (line.trim()) {
        try {
          // Try to parse as JSON (expecting structured output from Python)
          const modelData = JSON.parse(line.trim());
          this.processModelSignal(modelData);
        } catch (error) {
          // If not JSON, treat as regular log output
          console.log('📝 Model Log:', line.trim());
        }
      }
    }
  }

  /**
   * 🎯 Process model signal
   */
  private async processModelSignal(data: any): Promise<void> {
    try {
      const modelOutput: ModelOutput = {
        timestamp: new Date().toISOString(),
        signal: data.signal || 'HOLD',
        confidence: data.confidence || 0.5,
        price: data.price || 200.0,
        reasoning: data.reasoning || 'Model prediction'
      };

      console.log('🎯 Model Signal:', {
        signal: modelOutput.signal,
        confidence: `${(modelOutput.confidence * 100).toFixed(1)}%`,
        price: `$${modelOutput.price.toFixed(2)}`
      });

      // Save to CSV
      await this.saveToCsv(modelOutput);
      
      // Send to webhook
      await this.sendToWebhook(modelOutput);
      
    } catch (error) {
      console.error('❌ Error processing model signal:', error);
    }
  }

  /**
   * 💾 Save output to CSV file
   */
  private async saveToCsv(output: ModelOutput): Promise<void> {
    const csvLine = `${output.timestamp},${output.signal},${output.confidence},${output.price},"${output.reasoning || ''}"\n`;
    
    try {
      await fs.promises.appendFile(this.logFilePath, csvLine);
      console.log('💾 Saved to CSV:', this.logFilePath);
    } catch (error) {
      console.error('❌ Error saving to CSV:', error);
    }
  }

  /**
   * 🔗 Send to webhook interface
   */
  private async sendToWebhook(output: ModelOutput): Promise<void> {
    const payload: WebhookPayload = {
      type: 'model_signal',
      data: output,
      timestamp: new Date().toISOString()
    };

    try {
      const response = await axios.post(this.webhookUrl, payload, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 5000
      });
      
      console.log('🔗 Webhook sent:', response.status);
    } catch (error) {
      console.warn('⚠️  Webhook failed (server may not be running):', (error as any).message);
    }
  }

  /**
   * 📁 Ensure log directory exists
   */
  private ensureLogDirectory(): void {
    const logDir = path.dirname(this.logFilePath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
      console.log('📁 Created log directory:', logDir);
    }
  }

  /**
   * 📄 Initialize CSV file with headers
   */
  private initializeCsvFile(): void {
    if (!fs.existsSync(this.logFilePath)) {
      const headers = 'timestamp,signal,confidence,price,reasoning\n';
      fs.writeFileSync(this.logFilePath, headers);
      console.log('📄 Initialized CSV file with headers');
    } else {
      console.log('📄 Using existing CSV file');
    }
  }

  /**
   * 🔄 Keep the process alive
   */
  private keepAlive(): void {
    setInterval(() => {
      if (this.isRunning) {
        console.log(`⏰ Model Reader alive - ${new Date().toLocaleTimeString()}`);
      }
    }, 30000); // Log every 30 seconds
  }

  /**
   * 🛑 Stop the model reader
   */
  stop(): void {
    console.log('🛑 Stopping Model Reader...');
    
    if (this.pythonProcess) {
      this.pythonProcess.kill('SIGTERM');
      this.pythonProcess = null;
    }
    
    this.isRunning = false;
    console.log('✅ Model Reader stopped');
  }
}

// 🚀 Main execution
async function main() {
  const modelReader = new ModelReader();
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...');
    modelReader.stop();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
    modelReader.stop();
    process.exit(0);
  });

  // Start the model reader
  await modelReader.start();
}

// Run if this file is executed directly
if (require.main === module) {
  main().catch(console.error);
}

export { ModelReader, ModelOutput, WebhookPayload };
