import { useState, useRef } from 'react';
import { Send, Upload, FileText, Settings, Brain, Moon } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gpt-3.5-turbo');
  const [systemMessage, setSystemMessage] = useState('You are a helpful AI assistant. You are brutally honest, but kind. But you make sure everything you say is correct, scientifically validated, and true. You prioritise being factual and honest above everything');
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isRAGMode, setIsRAGMode] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [ragStatus, setRagStatus] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('https://ai-vibe-backend-qj2uw5sn0-tyroneinozs-projects.vercel.app/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: inputMessage,
          developer_message: systemMessage,
          model: model,
          api_key: apiKey || ""
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      let aiResponse = '';
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '',
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                aiResponse += parsed.content;
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === aiMessage.id 
                      ? { ...msg, content: aiResponse }
                      : msg
                  )
                );
              }
            } catch (e) {
              // Ignore parsing errors
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, there was an error processing your request.',
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadedFile(file);
    setIsUploading(true);
    setRagStatus('Uploading PDF...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('https://ai-vibe-backend-qj2uw5sn0-tyroneinozs-projects.vercel.app/api/upload-pdf', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setRagStatus(`PDF uploaded successfully! ${result.chunks} chunks processed.`);
      } else {
        setRagStatus('Failed to upload PDF');
      }
    } catch (error) {
      setRagStatus('Error uploading PDF');
    } finally {
      setIsUploading(false);
    }
  };

  const sendRAGMessage = async () => {
    if (!inputMessage.trim() || isLoading || !uploadedFile) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('https://ai-vibe-backend-qj2uw5sn0-tyroneinozs-projects.vercel.app/api/rag-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          api_key: apiKey || ""
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send RAG message');
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      let aiResponse = '';
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '',
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                aiResponse += parsed.content;
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === aiMessage.id 
                      ? { ...msg, content: aiResponse }
                      : msg
                  )
                );
              }
            } catch (e) {
              // Ignore parsing errors
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, there was an error processing your RAG request.',
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (isRAGMode) {
        sendRAGMessage();
      } else {
        sendMessage();
      }
    }
  };

  const clearUploadedFile = () => {
    setUploadedFile(null);
    setRagStatus('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">
              🧠 AI RAG Chat Application
            </h1>
            <p className="text-blue-200">
              {isRAGMode ? 'Dream Research Mode - Upload PDFs for specialized dream interpretation' : 'Chat with AI using your own API key'}
            </p>
          </div>

          {/* Dream Research Mode Toggle */}
          <div className="mb-6 flex justify-center">
            <button
              onClick={() => setIsRAGMode(!isRAGMode)}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                isRAGMode
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-gray-600 text-gray-200 hover:bg-gray-500'
              }`}
            >
              <Moon className="w-5 h-5" />
              {isRAGMode ? 'Dream Research Mode ON' : 'Enable Dream Research Mode'}
            </button>
          </div>

          {/* PDF Upload Section */}
          {isRAGMode && (
            <div className="mb-6 p-4 bg-white/10 rounded-lg backdrop-blur-sm">
              <div className="flex items-center gap-4 mb-4">
                <Upload className="w-6 h-6 text-blue-300" />
                <h3 className="text-lg font-semibold text-white">Upload Dream Research PDF</h3>
              </div>
              
              <div className="flex items-center gap-4">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="pdf-upload"
                />
                <label
                  htmlFor="pdf-upload"
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  Choose PDF
                </label>
                
                {uploadedFile && (
                  <div className="flex items-center gap-2">
                    <span className="text-green-300 text-sm">
                      ✓ {uploadedFile.name}
                    </span>
                    <button
                      onClick={clearUploadedFile}
                      className="text-red-300 hover:text-red-200 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                )}
              </div>
              
              {ragStatus && (
                <div className="mt-2 text-sm text-blue-200">
                  {ragStatus}
                </div>
              )}
            </div>
          )}

          {/* Settings Panel */}
          <div className="mb-6">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition-colors"
            >
              <Settings className="w-4 h-4" />
              Settings
            </button>
            
            {showSettings && (
              <div className="mt-4 p-4 bg-white/10 rounded-lg backdrop-blur-sm">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      OpenAI API Key (Optional - will use server fallback)
                    </label>
                    <input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="sk-..."
                    />
                    {apiKey && (
                      <p className="text-green-300 text-sm mt-1">✓ API Key provided</p>
                    )}
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Model
                    </label>
                    <select
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                      className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                      <option value="gpt-4">GPT-4</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      System Message
                    </label>
                    <textarea
                      value={systemMessage}
                      onChange={(e) => setSystemMessage(e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Chat Messages */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-6 min-h-[400px] max-h-[600px] overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-center text-gray-300 py-8">
                <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>
                  {isRAGMode 
                    ? 'Upload a PDF and start asking questions about dream research!'
                    : 'Start a conversation with the AI assistant!'
                  }
                </p>
                {isRAGMode && !uploadedFile && (
                  <p className="text-yellow-300 mt-2">
                    Please upload a PDF first to enable RAG functionality.
                  </p>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${
                        message.isUser
                          ? 'bg-blue-600 text-white'
                          : 'bg-white/20 text-white'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white/20 text-white p-3 rounded-lg">
                      <div className="flex items-center gap-2">
                        <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                        Thinking...
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="flex gap-4">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                isRAGMode 
                  ? (uploadedFile ? "Ask about the uploaded dream research..." : "Upload a PDF first...")
                  : "Type your message here..."
              }
              disabled={isLoading || (isRAGMode && !uploadedFile)}
              className="flex-1 px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={2}
            />
            <button
              onClick={isRAGMode ? sendRAGMessage : sendMessage}
              disabled={isLoading || !inputMessage.trim() || (isRAGMode && !uploadedFile)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
