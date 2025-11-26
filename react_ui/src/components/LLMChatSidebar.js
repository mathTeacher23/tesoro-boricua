import React, { useState } from 'react';

const LLMChatSidebar = ({ isOpen, onToggle, otherSidebarOpen }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = React.useRef(null);

  const API_BASE_URL = 'http://localhost:8000';

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) {
      setError('Please enter a message');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Add user message to chat
      const userMessage = { role: 'user', content: inputText };
      setMessages([...messages, userMessage]);
      setInputText('');

      // Send to backend
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputText,
          context: 'You are a helpful assistant about Puerto Rican culture, cuisine, language, and traditions. Provide informative and engaging responses.',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Chat failed');
      }

      const data = await response.json();
      const assistantMessage = { role: 'assistant', content: data.response };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      setError(
        err && err.message
          ? err.message
          : 'Failed to connect to LLM. Make sure LM Studio is running on port 1234.'
      );
      // Remove the user message if there was an error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setInputText('');
    setError(null);
  };

  return (
    <>
      {/* Toggle Button */}
      {!isOpen && (
        <button
          className={`translation-toggle ${isOpen ? 'open' : ''}`}
          onClick={onToggle}
          title="Toggle LLM Chat"
          style={{
            position: 'fixed',
            top: '40px',
            right: otherSidebarOpen ? '370px' : '80px',
            borderRadius: '8px',
            zIndex: '1001',
            padding: '10px 12px',
            transition: 'right 0.3s ease-in-out',
            background: '#6f42c1',
            color: '#fff',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          Bori-Bot 🐸
        </button>
      )}

      {/* Chat Sidebar */}
      <div
        className={`translation-sidebar ${isOpen ? 'open' : ''}`}
        style={{
          position: 'fixed',
          right: isOpen ? '0' : '-350px',
          top: '0',
          height: '100vh',
          width: '350px',
          zIndex: '999',
          transition: 'right 0.3s ease-in-out',
          boxShadow: '-2px 0 10px rgba(0,0,0,0.1)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          background: '#fff'
        }}
      >
        <div className="sidebar-header" style={{ background: '#6f42c1', padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, color: '#fff' }}>
            Bori-Bot 🐸
          </h3>
          <button
            type="button"
            className="close-btn"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onToggle();
            }}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#fff',
              fontSize: '24px',
              cursor: 'pointer',
              padding: '0',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>

        {/* Chat History - Scrollable Content Area */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', paddingRight: '4px' }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#6c757d', padding: '2rem 0' }}>
              <p>
                <i className="fas fa-comments" style={{ fontSize: '2rem', marginBottom: '1rem' }} />
              </p>
              <p>Start a conversation with the Bori-Bot</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  marginBottom: '1rem',
                  padding: '0.75rem',
                  borderRadius: '6px',
                  background: msg.role === 'user' ? '#e7f3ff' : '#f0f0f0',
                  borderLeft: `4px solid ${msg.role === 'user' ? '#007bff' : '#6f42c1'}`,
                }}
              >
                <strong style={{ color: msg.role === 'user' ? '#0056b3' : '#4a235a', fontSize: '0.85rem' }}>
                  {msg.role === 'user' ? 'You' : 'Bori-Bot 🐸'}
                </strong>
                <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem', color: '#333' }}>{msg.content}</p>
              </div>
            ))
          )}

          {/* Error Display */}
          {error && (
            <div className="translation-error" style={{ marginTop: '1rem' }}>
              <i className="fas fa-exclamation-triangle"></i>
              {error}
            </div>
          )}

          {/* Auto-scroll anchor point */}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area - Anchored to Bottom */}
        <div style={{ borderTop: '1px solid #dee2e6', padding: '1rem', background: '#fff' }}>
          <div className="translation-input" style={{ marginBottom: '0.5rem' }}>
            <label style={{ fontSize: '0.9rem', marginBottom: '0.5rem', display: 'block' }}>Your message:</label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Type your message... (Shift+Enter for new line)"
              rows={3}
              maxLength={500}
              disabled={isLoading}
              style={{
                width: '100%',
                borderRadius: '6px',
                border: '1px solid #dee2e6',
                padding: '0.5rem',
                fontFamily: 'inherit',
                resize: 'none',
                opacity: isLoading ? 0.6 : 1,
                cursor: isLoading ? 'not-allowed' : 'text',
              }}
            />
            <div className="char-count" style={{ fontSize: '0.75rem', color: '#6c757d', marginTop: '0.25rem' }}>
              {inputText.length}/500
            </div>
          </div>

          {/* Controls */}
          <div className="translation-controls" style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="btn btn-primary"
              onClick={handleSendMessage}
              disabled={isLoading || !inputText.trim()}
              title="Send message to Bori-Bot"
              style={{ flex: 1, padding: '0.5rem 1rem', background: '#6f42c1', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
            >
              <i className={`fas ${isLoading ? 'fa-spinner fa-spin' : 'fa-paper-plane'}`}></i>
              {isLoading ? 'Sending...' : 'Send'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleClear}
              disabled={isLoading}
              title="Clear chat history"
              style={{ flex: 1, padding: '0.5rem 1rem', background: '#6c757d', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
            >
              <i className="fas fa-eraser"></i> Clear
            </button>
          </div>
        </div>
      </div>

      {/* Backdrop */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: '0',
            left: '0',
            right: '350px',
            bottom: '0',
            background: 'rgba(0, 0, 0, 0.3)',
            zIndex: '998',
            onClick: onToggle
          }}
        ></div>
      )}
    </>
  );
};

export default LLMChatSidebar;
