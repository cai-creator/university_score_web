// WebSocket工具类
class WebSocketClient {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // 1秒
    this.eventHandlers = new Map();
    this.token = null;
  }

  // 连接WebSocket服务器
  connect() {
    if (this.socket && this.isConnected) {
      return;
    }

    // 获取token
    this.token = this.getToken();
    if (!this.token) {
      console.error('WebSocket连接失败：缺少token');
      return;
    }

    // 构建WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/advisor-allocation/?token=${this.token}`;

    try {
      this.socket = new WebSocket(wsUrl);

      // 连接打开事件
      this.socket.onopen = () => {
        console.log('WebSocket连接成功');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.emit('connected');
      };

      // 接收消息事件
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket接收消息:', data);
          
          if (data.type && data.data) {
            this.emit(data.type, data.data);
          } else {
            this.emit('message', data);
          }
        } catch (error) {
          console.error('WebSocket消息解析失败:', error);
          this.emit('error', error);
        }
      };

      // 连接关闭事件
      this.socket.onclose = () => {
        console.log('WebSocket连接关闭');
        this.isConnected = false;
        this.emit('disconnected');
        this.attemptReconnect();
      };

      // 连接错误事件
      this.socket.onerror = (error) => {
        console.error('WebSocket连接错误:', error);
        this.emit('error', error);
      };
    } catch (error) {
      console.error('WebSocket连接初始化失败:', error);
      this.emit('error', error);
    }
  }

  // 断开WebSocket连接
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
      this.reconnectAttempts = 0;
    }
  }

  // 尝试重新连接
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // 指数退避
      
      console.log(`WebSocket尝试重新连接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})，${delay}ms后重试`);
      
      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error('WebSocket重新连接失败，已达到最大尝试次数');
      this.emit('reconnect_failed');
    }
  }

  // 发送消息
  send(data) {
    if (this.socket && this.isConnected) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        this.socket.send(message);
        return true;
      } catch (error) {
        console.error('WebSocket发送消息失败:', error);
        this.emit('error', error);
        return false;
      }
    } else {
      console.error('WebSocket未连接，无法发送消息');
      return false;
    }
  }

  // 注册事件监听器
  on(event, callback) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event).push(callback);
  }

  // 移除事件监听器
  off(event, callback) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event);
      const index = handlers.indexOf(callback);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
      if (handlers.length === 0) {
        this.eventHandlers.delete(event);
      }
    }
  }

  // 触发事件
  emit(event, data) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event);
      handlers.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`WebSocket事件处理失败 (${event}):`, error);
        }
      });
    }
  }

  // 获取token
  getToken() {
    // 从localStorage获取token
    let token = localStorage.getItem('token');
    if (!token) {
      // 从sessionStorage获取token
      token = sessionStorage.getItem('token');
    }
    if (!token) {
      // 从cookie获取token
      const cookies = document.cookie.split('; ');
      for (const cookie of cookies) {
        const [name, value] = cookie.split('=');
        if (name === 'token') {
          token = decodeURIComponent(value);
          break;
        }
      }
    }
    return token;
  }

  // 检查连接状态
  getConnectionStatus() {
    return this.isConnected;
  }
}

// 创建单例实例
const websocketClient = new WebSocketClient();

export default websocketClient;
