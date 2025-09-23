/**
 * AI-Powered RAG Chat Application - Frontend Interface
 * ===================================================
 * 
 * This is the main user interface for our AI chat application.
 * Think of it as the "face" of our system - what users see and interact with.
 * 
 * WHAT THIS APPLICATION DOES:
 * - Provides a chat interface for talking with AI
 * - Allows users to upload PDF documents
 * - Enables asking questions about uploaded documents (RAG functionality)
 * - Shows real-time streaming responses from the AI
 * 
 * HOW IT WORKS (Simple Explanation):
 * 1. User types a message or uploads a PDF
 * 2. Frontend sends the data to our backend server
 * 3. Backend processes the request and sends back a response
 * 4. Frontend displays the response in real-time
 * 
 * This file contains all the React components and logic that make the user interface work.
 */

// =============================================================================
// IMPORTING NECESSARY TOOLS AND LIBRARIES
// =============================================================================

import { useState, useRef } from 'react';
// React hooks for managing state and references
// useState: Lets us store and update data (like remembering what the user typed)
// useRef: Lets us reference HTML elements (like scrolling to the bottom of chat)

import { Send, Upload, FileText, Settings, Brain, Moon } from 'lucide-react';
// Lucide React: A library of beautiful icons
// These icons make our interface look professional and intuitive

// =============================================================================
// DEFINING DATA STRUCTURES
// =============================================================================

interface Message {
  /**
   * This defines what a chat message looks like.
   * Think of it as a template for storing conversation history.
   * 
   * Each message has:
   * - id: A unique identifier (like a serial number)
   * - content: The actual text of the message
   * - isUser: Whether this message came from the user (true) or AI (false)
   * - timestamp: When the message was sent
   */
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

// =============================================================================
// MAIN COMPONENT - THE HEART OF OUR APPLICATION
// =============================================================================

export default function Home() {
  /**
   * This is the main component of our application.
   * It's like the control center that manages everything the user sees and does.
   * 
   * WHAT IT MANAGES:
   * - Chat messages and conversation history
   * - User settings (API key, model selection, etc.)
   * - PDF upload functionality
   * - RAG mode (document-based chat)
   * - Real-time streaming responses
   */

  // =============================================================================
  // STATE MANAGEMENT - KEEPING TRACK OF DATA
  // =============================================================================
  
  // Chat-related state
  const [messages, setMessages] = useState<Message[]>([]);
  // messages: Stores all the chat messages (user and AI responses)
  // setMessages: Function to update the messages list
  
  const [inputMessage, setInputMessage] = useState('');
  // inputMessage: What the user is currently typing
  // setInputMessage: Function to update the input field
  
  const [isLoading, setIsLoading] = useState(false);
  // isLoading: Whether we're waiting for a response from the AI
  // This shows loading indicators to the user
  
  // Settings-related state
  const [apiKey, setApiKey] = useState('');
  // apiKey: The user's OpenAI API key (optional - we have a fallback)
  
  const [model, setModel] = useState('gpt-3.5-turbo');
  // model: Which AI model to use (like choosing between different AI assistants)
  
  const [systemMessage, setSystemMessage] = useState(
    'You are a helpful AI assistant. You are brutally honest, but kind. But you make sure everything you say is correct, scientifically validated, and true. You prioritise being factual and honest above everything'
  );
  // systemMessage: Instructions for how the AI should behave
  // This is like giving the AI a personality and guidelines
  
  const [showSettings, setShowSettings] = useState(false);
  // showSettings: Whether to show the settings panel
  
  // RAG (Document-based chat) state
  const [isRAGMode, setIsRAGMode] = useState(false);
  // isRAGMode: Whether we're in "Dream Research Mode" (document-based chat)
  
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  // uploadedFile: The PDF file the user uploaded
  
  const [isUploading, setIsUploading] = useState(false);
  // isUploading: Whether we're currently uploading a PDF
  
  const [ragStatus, setRagStatus] = useState('');
  // ragStatus: Status messages about PDF upload and processing
  
  // UI reference for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // messagesEndRef: Reference to the bottom of the chat area
  // This lets us automatically scroll to new messages

  // =============================================================================
  // UTILITY FUNCTIONS
  // =============================================================================

  const scrollToBottom = () => {
    /**
     * Automatically scrolls the chat to the bottom.
     * This ensures users always see the latest messages.
     * It's like automatically turning to the last page of a book.
     */
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // =============================================================================
  // CHAT FUNCTIONALITY
  // =============================================================================

  const sendMessage = async () => {
    /**
     * Handles sending regular chat messages to the AI.
     * This is for general conversation, not document-based questions.
     * 
     * HOW IT WORKS:
     * 1. Check if there's a message to send
     * 2. Add the user's message to the chat
     * 3. Send the message to our backend
     * 4. Stream the AI's response back in real-time
     * 5. Update the chat with the AI's response
     */
    
    // Don't send empty messages or if we're already loading
    if (!inputMessage.trim() || isLoading) return;

    // Create a message object for the user's input
    const userMessage: Message = {
      id: Date.now().toString(), // Unique ID based on current time
      content: inputMessage,
      isUser: true, // This is from the user
      timestamp: new Date(),
    };

    // Add the user's message to the chat
    setMessages(prev => [...prev, userMessage]);
    setInputMessage(''); // Clear the input field
    setIsLoading(true); // Show loading indicator

    try {
      // Send the message to our backend server
      const response = await fetch('https://ai-vibe-backend-qj2uw5sn0-tyroneinozs-projects.vercel.app/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: inputMessage,
          developer_message: systemMessage,
          model: model,
          api_key: apiKey || "" // Use user's API key or empty string (backend has fallback)
        }),
      });

      // Check if the request was successful
      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      // Get the streaming response reader
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      // Prepare to receive the AI's response
      let aiResponse = '';
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '', // Start with empty content
        isUser: false, // This is from the AI
        timestamp: new Date(),
      };

      // Add the AI message to chat (initially empty)
      setMessages(prev => [...prev, aiMessage]);

      // Read the streaming response chunk by chunk
      while (true) {
        const { done, value } = await reader.read();
        if (done) break; // Stop when we've read everything

        // Convert the chunk to text
        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');
        
        // Process each line of the response
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6); // Remove 'data: ' prefix
            
            if (data === '[DONE]') continue; // Skip completion signal
            
            try {
              // Parse the JSON data
              const parsed = JSON.parse(data);
              if (parsed.content) {
                // Add this chunk to the AI's response
                aiResponse += parsed.content;
                
                // Update the AI message in real-time
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === aiMessage.id 
                      ? { ...msg, content: aiResponse }
                      : msg
                  )
                );
              }
            } catch (e) {
              // Ignore parsing errors (sometimes we get incomplete data)
            }
          }
        }
      }
    } catch (error) {
      // Handle errors gracefully
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: `Error: ${error instanceof Error ? error.message : 'Something went wrong'}`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      // Always stop loading when done
      setIsLoading(false);
      // Scroll to the bottom to show the new message
      setTimeout(scrollToBottom, 100);
    }
  };

  // =============================================================================
  // PDF UPLOAD FUNCTIONALITY
  // =============================================================================

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    /**
     * Handles uploading PDF files to our backend.
     * This is the first step in enabling document-based chat (RAG).
     * 
     * HOW IT WORKS:
     * 1. User selects a PDF file
     * 2. We create a FormData object with the file
     * 3. We send it to our backend for processing
     * 4. Backend extracts text and stores it for later use
     * 5. We show the user that the upload was successful
     */
    
    const file = event.target.files?.[0];
    if (!file) return; // No file selected

    // Check if it's actually a PDF
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setRagStatus('Please select a PDF file.');
      return;
    }

    setIsUploading(true); // Show uploading indicator
    setRagStatus('Uploading PDF...');

    // Create FormData to send the file
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Send the file to our backend
      const response = await fetch('https://ai-vibe-backend-qj2uw5sn0-tyroneinozs-projects.vercel.app/api/upload-pdf', {
        method: 'POST',
        body: formData, // Send the file
      });

      if (response.ok) {
        // Success! Update our state
        const result = await response.json();
        setUploadedFile(file);
        setRagStatus(`PDF uploaded successfully: ${result.filename}`);
        setIsRAGMode(true); // Automatically switch to RAG mode
      } else {
        // Handle errors
        const errorText = await response.text();
        setRagStatus(`Upload failed: ${errorText}`);
      }
    } catch (error) {
      // Handle network errors
      setRagStatus(`Error uploading PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false); // Stop uploading indicator
    }
  };

  // =============================================================================
  // RAG CHAT FUNCTIONALITY
  // =============================================================================

  const sendRAGMessage = async () => {
    /**
     * Handles sending questions about uploaded documents.
     * This is the core of our RAG (Retrieval-Augmented Generation) functionality.
     * 
     * HOW IT WORKS:
     * 1. User asks a question about the uploaded document
     * 2. We send the question to our backend
     * 3. Backend searches through the document for relevant information
     * 4. Backend combines the relevant info with the question
     * 5. AI generates an answer based on the document content
     * 6. We stream the answer back to the user
     */
    
    if (!inputMessage.trim() || isLoading) return;

    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      isUser: true,
      timestamp: new Date(),
    };

    // Add to chat and clear input
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send RAG request to backend
      const response = await fetch('https://ai-vibe-backend-qj2uw5sn0-tyroneinozs-projects.vercel.app/api/rag-chat', {
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
        throw new Error('Failed to send RAG message');
      }

      // Handle streaming response (same as regular chat)
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
      console.error('Error sending RAG message:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: `Error: ${error instanceof Error ? error.message : 'Something went wrong'}`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setTimeout(scrollToBottom, 100);
    }
  };

  // =============================================================================
  // EVENT HANDLERS
  // =============================================================================

  const handleKeyPress = (e: React.KeyboardEvent) => {
    /**
     * Handles the Enter key press in the input field.
     * This makes the chat feel more natural - users can press Enter to send messages.
     */
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent adding a new line
      if (isRAGMode) {
        sendRAGMessage(); // Send RAG message if in document mode
      } else {
        sendMessage(); // Send regular message
      }
    }
  };

  const clearUploadedFile = () => {
    /**
     * Clears the uploaded file and switches back to regular chat mode.
     * This is like closing a document and going back to general conversation.
     */
    setUploadedFile(null);
    setIsRAGMode(false);
    setRagStatus('');
  };

  // =============================================================================
  // USER INTERFACE RENDERING
  // =============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Main Container */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🤖 AI-Powered RAG Chat
          </h1>
          <p className="text-gray-600">
            Chat with AI or upload documents for intelligent Q&A
          </p>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Settings className="mr-2" />
              Settings
            </h3>
            
            <div className="space-y-4">
              {/* API Key Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  OpenAI API Key (Optional)
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your OpenAI API key (optional - we have a fallback)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Leave empty to use our server's API key
                </p>
              </div>

              {/* Model Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  AI Model
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                </select>
              </div>

              {/* System Message */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  System Message (AI Personality)
                </label>
                <textarea
                  value={systemMessage}
                  onChange={(e) => setSystemMessage(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Instructions for how the AI should behave..."
                />
              </div>
            </div>
          </div>
        )}

        {/* RAG Controls */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center">
              <Brain className="mr-2" />
              Dream Research Mode
            </h3>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>

          {/* RAG Mode Toggle */}
          <div className="flex items-center space-x-4 mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isRAGMode}
                onChange={(e) => setIsRAGMode(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm font-medium">Enable Document-Based Chat</span>
            </label>
          </div>

          {/* PDF Upload */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload PDF Document
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>

            {/* Upload Status */}
            {ragStatus && (
              <div className={`p-3 rounded-md text-sm ${
                ragStatus.includes('successfully') 
                  ? 'bg-green-50 text-green-700 border border-green-200' 
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}>
                {ragStatus}
              </div>
            )}

            {/* Uploaded File Info */}
            {uploadedFile && (
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-md">
                <div className="flex items-center">
                  <FileText className="w-5 h-5 text-blue-600 mr-2" />
                  <span className="text-sm font-medium text-blue-800">
                    {uploadedFile.name}
                  </span>
                </div>
                <button
                  onClick={clearUploadedFile}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Chat Interface */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Chat Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <p className="text-lg mb-2">👋 Welcome to AI Chat!</p>
                <p className="text-sm">
                  {isRAGMode 
                    ? "Upload a PDF and ask questions about it, or switch to regular chat mode."
                    : "Start a conversation or enable Dream Research Mode to chat with documents."
                  }
                </p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.isUser
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      message.isUser ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t p-4">
            <div className="flex space-x-2">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  isRAGMode 
                    ? "Ask a question about your uploaded document..." 
                    : "Type your message here..."
                }
                disabled={isLoading || (isRAGMode && !uploadedFile)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={2}
              />
              <button
                onClick={isRAGMode ? sendRAGMessage : sendMessage}
                disabled={isLoading || !inputMessage.trim() || (isRAGMode && !uploadedFile)}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
            
            {/* Status Messages */}
            {isRAGMode && !uploadedFile && (
              <p className="text-sm text-amber-600 mt-2">
                ⚠️ Please upload a PDF document to use Dream Research Mode
              </p>
            )}
            
            {apiKey && (
              <p className="text-sm text-green-600 mt-2">
                ✅ Using your personal API key
              </p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>
            Powered by OpenAI • Built with Next.js and FastAPI • 
            <a href="https://github.com/TyroneTheCodeChainer/AIE08_MyAwesomeRep" 
               className="text-blue-500 hover:text-blue-700 ml-1">
              View Source Code
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}