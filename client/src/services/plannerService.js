import api, { API_BASE_URL } from './api';

export const plannerService = {
  /**
   * Start autonomous planner streaming with retry logic, timeout, error catching, and offline detection.
   * @param {Object} payload 
   * @param {Function} onEventCallback 
   * @param {Function} [onErrorCallback]
   */
  async startPlannerStream(payload, onEventCallback, onErrorCallback) {
    const token = localStorage.getItem('tripgenie_token');
    
    // Resolve full endpoint URL safely
    let targetUrl = '/api/v1/planner/start';
    if (API_BASE_URL && API_BASE_URL.startsWith('http')) {
      targetUrl = `${API_BASE_URL}/planner/start`;
    }

    const MAX_RETRIES = 2;
    let attempt = 0;
    let response = null;
    let lastError = null;

    while (attempt <= MAX_RETRIES) {
      attempt++;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout for stream initiation/response

      try {
        response = await fetch(targetUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
          },
          body: JSON.stringify(payload),
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response && response.ok) {
          break; // Success! Break retry loop
        } else {
          lastError = new Error(`HTTP Error ${response?.status || 'Unknown'}`);
        }
      } catch (err) {
        clearTimeout(timeoutId);
        lastError = err;
        // If aborted due to timeout or network error, wait before retry
        if (attempt <= MAX_RETRIES) {
          await new Promise(res => setTimeout(res, 1500 * attempt));
        }
      }
    }

    // If fetch failed after retries or server returned error status
    if (!response || !response.ok) {
      const offlineMsg = "Backend server is offline.";
      const errorLog = {
        agent_name: "System Error",
        status: "failed",
        error: true,
        message: offlineMsg,
        detail: lastError ? (lastError.message || String(lastError)) : "Network connection failed"
      };

      if (typeof onEventCallback === 'function') {
        onEventCallback(errorLog);
      }
      if (typeof onErrorCallback === 'function') {
        onErrorCallback(errorLog);
      }

      return {
        success: false,
        error: offlineMsg,
        detail: lastError ? (lastError.message || String(lastError)) : offlineMsg
      };
    }

    // Read SSE stream safely
    try {
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // save incomplete line

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const dataJson = JSON.parse(line.replace('data: ', ''));
              if (typeof onEventCallback === 'function') {
                onEventCallback(dataJson);
              }
            } catch (err) {
              console.error('Error parsing SSE event', err);
            }
          }
        }
      }
      
      return { success: true };
    } catch (streamErr) {
      console.error('Error reading stream body', streamErr);
      const streamErrorLog = {
        agent_name: "Stream Error",
        status: "failed",
        error: true,
        message: "Connection lost while generating plan."
      };
      if (typeof onEventCallback === 'function') {
        onEventCallback(streamErrorLog);
      }
      return { success: false, error: "Connection lost while generating plan." };
    }
  },

  /**
   * Send chat message to assistant. Guaranteed to catch exceptions and return proper JSON.
   */
  async sendChatMessage(message, tripId) {
    try {
      const res = await api.post('/planner/chat', { message, trip_id: tripId });
      return res.data;
    } catch (err) {
      console.error("[plannerService] Chat error:", err);
      const isOffline = err.isOffline || err.code === 'ERR_NETWORK' || !err.response;
      const errorMsg = isOffline 
        ? "Backend server is offline."
        : (err.response?.data?.detail || err.response?.data?.message || err.message || "Failed to send message.");
      
      return {
        reply: `⚠️ ${errorMsg}`,
        agent_name: "TripGenie AI",
        intent: "ERROR",
        error: true,
        offline: isOffline
      };
    }
  }
};
