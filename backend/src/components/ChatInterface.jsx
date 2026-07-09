import React, { useState, useRef, useEffect } from 'react';
import api from '../services/api';

const ChatInterface = ({ selectedHCP }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your HCP CRM assistant. How can I help you log or manage HCP interactions?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/agent/chat', {
        message: input,
        hcp_id: selectedHCP?.id
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response
      };
      setMessages(prev => [...prev, assistantMessage]);

      // If there's tool result data, show it in a structured way
      if (response.data.data) {
        const toolResultMessage = {
          role: 'assistant',
          content: `📊 Tool Result: ${JSON.stringify(response.data.data, null, 2)}`,
          isToolResult: true
        };
        setMessages(prev => [...prev, toolResultMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role}`}
            style={message.isToolResult ? { 
              background: '#e8f4fd', 
              color: '#1a1a2e',
              fontFamily: 'monospace',
              fontSize: '12px',
              maxWidth: '100%'
            } : {}}
          >
            {message.content}
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <span className="typing-indicator">Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Describe interaction or ask for help..."
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;