#!/usr/bin/env ts-node

/**
 * 🦖 SIMPLE MODEL READER - TypeScript
 * ===================================
 * 
 * Simplified version that works standalone
 */

import { spawn, ChildProcess } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as http from 'http';

interface ModelOutput {
  timestamp: string;
  signal: 'BUY' | 'HOLD' | 'SELL';
  confidence: number;
  price: number;
  reasoning?: string;
}

class SimpleModelReader {
  private pythonProcess: ChildProcess | null = null;
  private isRunning: boolean = false;
  private logFilePath: string;
  private webhookUrl: string = 'http://localhost:5001/webhook';

  constructor() {
    this.logFilePath = path.join(process.cwd(), 'logs', 'model_output.csv');
    this.ensureLogDirectory();
    this.initializeCsvFile();
  }

  async start(): Promise<void> {
    console.log('🦖 Starting Simple Model Reader...');
    console.log('📁 Log file:', this.logFilePath);
    console.log('🔗 Webhook URL:', this.webhookUrl);
    
    try {
      await this.startPythonModel();
      this.isRunning = true;
      console.log('✅ Model Reader started successfully!');
      
      // Listen for real model outputs from Python process
      
      this.keepAlive();
    } catch (error) {
      console.error('❌ Failed to start Model Reader:', error);
      process.exit(1);
    }
  }

  private async startPythonModel(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log('🐍 Starting Python model process...');
      
      // Allow selecting which Python model to run (default: test_model.py)
      const modelScript = process.env.MODEL_SCRIPT || 'test_model.py';
      const pythonScript = path.join(process.cwd(), 'app', 'modules', 'model', modelScript);
      
      this.pythonProcess = spawn('python3', [pythonScript], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.join(process.cwd(), 'app', 'modules', 'model')
      });

      this.pythonProcess.stdout?.on('data', (data) => {
        const output = data.toString();
        console.log('🐍 Python Model:', output.trim());
        this.handleModelOutput(output);
      });

      this.pythonProcess.stderr?.on('data', (data) => {
        const error = data.toString();
        if (!error.includes('urllib3') && !error.includes('SSL')) {
          console.error('🐍 Python Error:', error.trim());
        }
      });

      this.pythonProcess.on('spawn', () => {
        console.log('✅ Python model process spawned successfully');
        resolve();
      });

      this.pythonProcess.on('error', (error) => {
        console.error('❌ Failed to spawn Python process:', error);
        reject(error);
      });
    });
  }

  private outputBuffer: string = '';

  private handleModelOutput(output: string): void {
    this.outputBuffer += output;
    
    // Process complete lines
    const lines = this.outputBuffer.split('\n');
    this.outputBuffer = lines.pop() || ''; // Keep incomplete line in buffer
    
    for (const line of lines) {
      if (line.trim()) {
        this.parseModelLine(line.trim());
      }
    }
  }

  private parseModelLine(line: string): void {
    try {
      // Look for JSON output from the model
      if (line.startsWith('{') && line.endsWith('}')) {
        const modelData = JSON.parse(line);
        this.processRealModelSignal(modelData);
        return;
      }

      // Look for your model's signal output: "Got signal: 0" or "Got signal: 1"
      if (line.includes('Got signal:')) {
        const signalMatch = line.match(/Got signal:\s*(\d+)/);
        if (signalMatch) {
          const prediction = parseInt(signalMatch[1]);
          console.log('🎯 REAL Model Signal Detected:', prediction === 1 ? 'BUY' : 'HOLD');
          this.processRealModelSignal({
            prediction: prediction,
            timestamp: new Date().toISOString(),
            source: 'real_model_output'
          });
        }
        return;
      }

      // Look for other prediction formats
      if (line.includes('Prediction:') || line.includes('Signal:')) {
        const prediction = this.extractPrediction(line);
        if (prediction !== null) {
          this.processRealModelSignal({
            prediction: prediction,
            timestamp: new Date().toISOString(),
            source: 'model_output'
          });
        }
        return;
      }

      // Look for other model outputs
      if (line.includes('BUY') || line.includes('HOLD') || line.includes('SELL')) {
        console.log('🎯 Model signal detected:', line);
        const signal = this.extractSignalFromText(line);
        if (signal) {
          this.processRealModelSignal({
            signal: signal,
            timestamp: new Date().toISOString(),
            source: 'text_output'
          });
        }
      }
    } catch (error) {
      // If not parseable, just log as regular output
      console.log('📝 Model Log:', line);
    }
  }

  private extractPrediction(line: string): number | null {
    const match = line.match(/(?:Prediction|Signal):\s*(\d+)/);
    return match ? parseInt(match[1]) : null;
  }

  private extractSignalFromText(line: string): 'BUY' | 'HOLD' | 'SELL' | null {
    if (line.includes('BUY')) return 'BUY';
    if (line.includes('HOLD')) return 'HOLD';
    if (line.includes('SELL')) return 'SELL';
    return null;
  }

  private processRealModelSignal(data: any): void {
    let signal: 'BUY' | 'HOLD' | 'SELL' = 'HOLD';
    let confidence = 0.5;
    let reasoning = 'Real model prediction';

    // Convert prediction number to signal
    if (data.prediction !== undefined) {
      signal = data.prediction === 1 ? 'BUY' : 'HOLD';
      confidence = data.confidence || 0.8;
      reasoning = `Model prediction: ${data.prediction} (${signal})`;
    } else if (data.signal) {
      signal = data.signal;
      confidence = data.confidence || 0.8;
      reasoning = data.reasoning || `Real ${signal} signal from model`;
    }

    const modelOutput: ModelOutput = {
      timestamp: data.timestamp || new Date().toISOString(),
      signal: signal,
      confidence: confidence,
      price: data.price || 200.0, // Default price if not provided
      reasoning: reasoning
    };

    console.log('🎯 REAL Model Signal:', {
      signal: modelOutput.signal,
      confidence: `${(modelOutput.confidence * 100).toFixed(1)}%`,
      price: `$${modelOutput.price.toFixed(2)}`,
      source: data.source || 'model'
    });

    this.saveToCsv(modelOutput);
    this.sendToWebhook(modelOutput);
  }

  private async saveToCsv(output: ModelOutput): Promise<void> {
    const csvLine = `${output.timestamp},${output.signal},${output.confidence},${output.price},"${output.reasoning || ''}"\n`;
    
    try {
      await fs.promises.appendFile(this.logFilePath, csvLine);
      console.log('💾 Saved to CSV');
    } catch (error) {
      console.error('❌ Error saving to CSV:', error);
    }
  }

  private sendToWebhook(output: ModelOutput): void {
    const payload = JSON.stringify({
      type: 'model_signal',
      data: output,
      timestamp: new Date().toISOString()
    });

    const options = {
      hostname: 'localhost',
      port: 5001,
      path: '/webhook',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    };

    const req = http.request(options, (res) => {
      console.log('🔗 Webhook response:', res.statusCode);
    });

    req.on('error', (error) => {
      console.warn('⚠️  Webhook failed:', error.message);
    });

    req.write(payload);
    req.end();
  }

  private ensureLogDirectory(): void {
    const logDir = path.dirname(this.logFilePath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
      console.log('📁 Created log directory:', logDir);
    }
  }

  private initializeCsvFile(): void {
    if (!fs.existsSync(this.logFilePath)) {
      const headers = 'timestamp,signal,confidence,price,reasoning\n';
      fs.writeFileSync(this.logFilePath, headers);
      console.log('📄 Initialized CSV file with headers');
    } else {
      console.log('📄 Using existing CSV file');
    }
  }

  private keepAlive(): void {
    setInterval(() => {
      if (this.isRunning) {
        console.log(`⏰ Model Reader alive - ${new Date().toLocaleTimeString()}`);
      }
    }, 30000);
  }

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
  const modelReader = new SimpleModelReader();
  
  process.on('SIGINT', () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...');
    modelReader.stop();
    process.exit(0);
  });

  await modelReader.start();
}

// Run the main function
main().catch(console.error);
