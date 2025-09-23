import { useState, useRef } from 'react';
import Head from 'next/head';
import { Send, Bot, User, Settings, Loader2, Upload, FileText, X } from 'lucide-react';

// Force deployment - fix API key message (v4)

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gpt-4.1-mini');
  const [developerMessage, setDeveloperMessage] = useState('You are a specialized dream interpretation assistant with expertise in sleep science, psychology, and neuroscience. You analyze dreams using scientifically validated research and provide insights based on REM sleep studies, Jungian psychology, and cognitive science. Always ground your interpretations in established research while being empathetic and supportive.');
  const [showSettings, setShowSettings] = useState(false);
  
  // RAG-related state
  const [isRAGMode, setIsRAGMode] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [ragStatus, setRagStatus] = useState({ pdf_uploaded: false, document_count: 0 });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          developer_message: developerMessage,
          user_message: input,
          model: model,
          api_key: apiKey || "" // Send empty string if no API key provided
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      const assistantMessageObj: Message = {
        role: 'assistant',
        content: '',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessageObj]);

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          assistantMessage += chunk;

          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              ...newMessages[newMessages.length - 1],
              content: assistantMessage
            };
            return newMessages;
          });
        }
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please check your API key and try again.',
        timestamp: new Date()
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

  // PDF upload function
  const handleFileUpload = async (file: File) => {
    // API key is now optional - backend will use environment variable

    setIsUploading(true);
    try {
      // First test with simple endpoint
      const formData = new FormData();
      formData.append('file', file);

      console.log('Testing simple upload endpoint...');
      const testResponse = await fetch('/api/test-upload', {
        method: 'POST',
        body: formData,
      });

      if (!testResponse.ok) {
        throw new Error('Test upload failed');
      }

      const testResult = await testResponse.json();
      console.log('Test upload successful:', testResult);

      // Now try the full RAG upload
      const ragFormData = new FormData();
      ragFormData.append('file', file);

      console.log('Testing RAG upload endpoint...');
      console.log('API Key length:', apiKey.length);
      console.log('API Key starts with:', apiKey.substring(0, 10) + '...');
      
      const response = await fetch(`/api/upload-pdf?api_key=${encodeURIComponent(apiKey || "")}`, {
        method: 'POST',
        body: ragFormData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('RAG upload failed:', response.status, errorText);
        throw new Error(`Failed to upload PDF: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      setUploadedFile(file);
      setRagStatus({ pdf_uploaded: true, document_count: result.document_count });
      alert(`PDF uploaded successfully! Indexed ${result.document_count} document chunks.`);
    } catch (error) {
      console.error('Error uploading PDF:', error);
      alert('Error uploading PDF. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // RAG chat function
  const sendRAGMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/rag-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: input,
          model: model,
          api_key: apiKey || "" // Send empty string if no API key provided
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const assistantMessage: Message = {
        role: 'assistant',
        content: '',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            content: newMessages[newMessages.length - 1].content + chunk
          };
          return newMessages;
        });
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please check your API key and try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Check RAG status on component mount
  const checkRAGStatus = async () => {
    try {
      const response = await fetch('/api/rag-status');
      if (response.ok) {
        const status = await response.json();
        setRagStatus(status);
      }
    } catch (error) {
      console.error('Error checking RAG status:', error);
    }
  };

  // Toggle RAG mode
  const toggleRAGMode = () => {
    setIsRAGMode(!isRAGMode);
    if (!isRAGMode) {
      checkRAGStatus();
    }
  };

  return (
    <>
      <Head>
        <title>AI Engineer Challenge - Chat Interface</title>
        <meta name="description" content="A modern chat interface powered by OpenAI" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-indigo-800 flex items-center">
                    🌙 Dream Interpretation Assistant
                  </h1>
                  <p className="text-indigo-600">Scientifically-Validated Dream Analysis</p>
                </div>
              </div>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
              >
                <Settings className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Settings Panel */}
          {showSettings && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-lg font-semibold mb-4 text-gray-900">Settings</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter your OpenAI API key"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model
                  </label>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  >
                    <option value="gpt-4.1-mini">GPT-4.1 Mini</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    System Message
                  </label>
                  <textarea
                    value={developerMessage}
                    onChange={(e) => setDeveloperMessage(e.target.value)}
                    placeholder="Enter the system message for the AI"
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  />
                </div>
                
                {/* RAG Mode Toggle */}
                <div className="border-t pt-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-medium text-indigo-900">📚 Dream Research Mode</h3>
                      <p className="text-sm text-indigo-600">Upload dream research papers for scientific analysis</p>
                    </div>
                    <button
                      onClick={toggleRAGMode}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        isRAGMode ? 'bg-indigo-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          isRAGMode ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                  
                  {isRAGMode && (
                    <div className="space-y-4">
                      {/* PDF Upload */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Upload PDF
                        </label>
                        <div className="flex items-center space-x-4">
                          <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf"
                            onChange={(e) => {
                              const file = e.target.files?.[0];
                              if (file) handleFileUpload(file);
                            }}
                            className="hidden"
                          />
                          <button
                            onClick={() => fileInputRef.current?.click()}
                            disabled={isUploading}
                            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                          >
                            {isUploading ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Upload className="w-4 h-4" />
                            )}
                            <span>{isUploading ? 'Uploading...' : 'Choose PDF'}</span>
                          </button>
                          
                          {uploadedFile && (
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <FileText className="w-4 h-4" />
                              <span>{uploadedFile.name}</span>
                              <button
                                onClick={() => {
                                  setUploadedFile(null);
                                  setRagStatus({ pdf_uploaded: false, document_count: 0 });
                                }}
                                className="text-red-500 hover:text-red-700"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          )}
                        </div>
                        
                        {ragStatus.pdf_uploaded && (
                          <p className="text-sm text-green-600 mt-2">
                            ✓ PDF indexed with {ragStatus.document_count} document chunks
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <div className="bg-white rounded-lg shadow-lg h-96 overflow-y-auto p-6 mb-6">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Start a conversation with the AI assistant</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex items-start space-x-2 max-w-xs lg:max-w-md ${
                        message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          message.role === 'user'
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-200 text-gray-600'
                        }`}
                      >
                        {message.role === 'user' ? (
                          <User className="w-4 h-4" />
                        ) : (
                          <Bot className="w-4 h-4" />
                        )}
                      </div>
                      <div
                        className={`px-4 py-2 rounded-lg ${
                          message.role === 'user'
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className="text-xs mt-1 opacity-70">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-2">
                      <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                        <Bot className="w-4 h-4" />
                      </div>
                      <div className="bg-gray-100 px-4 py-2 rounded-lg">
                        <Loader2 className="w-4 h-4 animate-spin" />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex space-x-4">
              <div className="flex-1">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={
                    isRAGMode 
                      ? "Describe your dream for scientific analysis... (Press Enter to send, Shift+Enter for new line)"
                      : "Describe your dream for interpretation... (Press Enter to send, Shift+Enter for new line)"
                  }
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-gray-900"
                  rows={3}
                  disabled={isLoading || (isRAGMode && !ragStatus.pdf_uploaded)}
                />
              </div>
              <button
                onClick={isRAGMode ? sendRAGMessage : sendMessage}
                disabled={isLoading || !input.trim() || (isRAGMode && !ragStatus.pdf_uploaded)}
                className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
                <span>Send</span>
              </button>
            </div>
            {!apiKey.trim() && (
              <p className="text-sm text-green-500 mt-2">
                ✅ Using server-configured API key. Ready to chat! (v2)
              </p>
            )}
            {isRAGMode && !ragStatus.pdf_uploaded && apiKey.trim() && (
              <p className="text-sm text-orange-500 mt-2">
                Please upload a PDF file to enable RAG chat functionality.
              </p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
