import React, { useState, useRef, useEffect } from 'react'
import './SupportChat.css'

function SupportChat() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendQuestion = async userMessage => {
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage }),
      })

      if (!response.ok) throw new Error('Network response was not ok')

      const data = await response.json()
      setMessages(prev => [...prev, { role: 'ai', content: data.answer }])
    } catch (error) {
      console.error('Error communicating with backend:', error)
      setMessages(prev => [
        ...prev,
        {
          role: 'error',
          content:
            'Sorry, there was an error processing your request. Please ensure the backend is running.',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = e => {
    e.preventDefault()
    if (!question.trim()) return
    const currentQuestion = question.trim()
    setQuestion('')
    sendQuestion(currentQuestion)
  }

  const handleQuickPrompt = promptText => {
    sendQuestion(promptText)
  }

  return (
    <div className='chat-container'>
      {/* Dynamic colorful header */}
      <div className='chat-header'>
        <div className='chat-header-info'>
          <div className='avatar-header'>🤖</div>
          <div>
            <h2>AI Support Assistant</h2>
            <p>
              <span className='status-dot'></span> Online • Ask about company
              policies
            </p>
          </div>
        </div>
      </div>

      <div className='chat-messages'>
        {messages.length === 0 && (
          <div className='empty-state'>
            <div className='empty-icon'>💡</div>
            <h3>How can I help you today?</h3>
            <p>Try asking one of these frequent questions:</p>
            <div className='quick-prompts'>
              <button
                onClick={() =>
                  handleQuickPrompt('What is our remote work policy?')
                }
              >
                🏡 Remote work policy
              </button>
              <button
                onClick={() =>
                  handleQuickPrompt('How do I submit expense reports?')
                }
              >
                🧾 Expense reports
              </button>
              <button
                onClick={() =>
                  handleQuickPrompt('What are the annual leave rules?')
                }
              >
                🌴 Annual leave
              </button>
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message-wrapper ${msg.role}`}>
            {msg.role !== 'user' && <div className='avatar ai-avatar'>🤖</div>}
            <div className={`message-bubble ${msg.role}`}>{msg.content}</div>
            {msg.role === 'user' && (
              <div className='avatar user-avatar'>👤</div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className='message-wrapper ai'>
            <div className='avatar ai-avatar'>🤖</div>
            <div className='message-bubble loading'>
              <span className='dot'></span>
              <span className='dot'></span>
              <span className='dot'></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className='chat-input-area'>
        <input
          type='text'
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder='Ask a policy question...'
          disabled={isLoading}
          className='chat-input'
        />
        <button
          type='submit'
          disabled={isLoading || !question.trim()}
          className='chat-submit-btn'
        >
          Send 🚀
        </button>
      </form>
    </div>
  )
}

export default SupportChat
