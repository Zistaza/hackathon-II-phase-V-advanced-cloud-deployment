/**
 * WebSocket service for real-time task updates
 * Connects to backend WebSocket endpoint and receives task events
 */

import { TaskEvent } from '../types/task';

export type WebSocketEventHandler = (event: TaskEvent) => void;

export class TaskWebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private eventHandlers: WebSocketEventHandler[] = [];
  private userId: string;
  private wsUrl: string;

  constructor(userId: string, wsUrl?: string) {
    this.userId = userId;
    // Default to backend WebSocket endpoint
    this.wsUrl = wsUrl || `ws://localhost:8000/ws/${userId}`;
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      };

      this.ws.onmessage = (event) => {
        try {
          const taskEvent: TaskEvent = JSON.parse(event.data);
          console.log('Received task event:', taskEvent.event_type);

          // Notify all registered handlers
          this.eventHandlers.forEach(handler => handler(taskEvent));
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.handleReconnect();
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.handleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Register an event handler
   */
  onEvent(handler: WebSocketEventHandler): () => void {
    this.eventHandlers.push(handler);

    // Return unsubscribe function
    return () => {
      this.eventHandlers = this.eventHandlers.filter(h => h !== handler);
    };
  }

  /**
   * Handle reconnection with exponential backoff
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
let wsServiceInstance: TaskWebSocketService | null = null;

/**
 * Get or create WebSocket service instance
 */
export function getWebSocketService(userId: string): TaskWebSocketService {
  if (!wsServiceInstance || wsServiceInstance['userId'] !== userId) {
    wsServiceInstance = new TaskWebSocketService(userId);
  }
  return wsServiceInstance;
}
