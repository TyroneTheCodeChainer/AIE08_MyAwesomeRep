# AI Engineer Challenge Frontend

A modern React/Next.js frontend for the AI Engineer Challenge application. This frontend provides a beautiful chat interface that integrates with the FastAPI backend to communicate with OpenAI's GPT models.

## Features

- 🎨 Modern, responsive UI with Tailwind CSS
- 💬 Real-time streaming chat interface
- ⚙️ Configurable settings (API key, model selection, system message)
- Real-time message streaming from OpenAI
- 📱 Mobile-friendly design
- 🎯 TypeScript support for better development experience
- Secure password input for API keys

## Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager
- Running FastAPI backend (see `/api` directory)

## Quick Start

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## Running the Complete Application

1. **Start the FastAPI backend** (in a separate terminal):
   ```bash
   cd ../api
   python app.py
   ```
   The backend will run on `http://localhost:8000`

2. **Start the frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

3. **Configure and use:**
   - Click the settings icon (⚙️) in the top-right corner
   - Enter your OpenAI API key (password field for security)
   - Select your preferred GPT model
   - Customize the system message
   - Start chatting!

## Usage

1. **Configure Settings**: Click the settings icon (⚙️) in the top-right corner
2. **Enter API Key**: Add your OpenAI API key in the secure password field
3. **Select Model**: Choose from available GPT models (GPT-4.1 Mini, GPT-4, GPT-3.5 Turbo)
4. **Customize System Message**: Set the behavior and personality of the AI
5. **Start Chatting**: Type your message and press Enter or click Send

## API Integration

The frontend communicates with the FastAPI backend through the following endpoints:

- `POST /api/chat` - Send messages and receive streaming responses
- `GET /api/health` - Health check endpoint

## Project Structure

```
frontend/
├── pages/
│   ├── index.tsx          # Main chat interface
│   └── _app.tsx          # App wrapper component
├── styles/
│   └── globals.css       # Global styles and Tailwind imports
├── package.json          # Dependencies and scripts
├── next.config.js        # Next.js configuration with API proxy
├── tailwind.config.js    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
├── postcss.config.js     # PostCSS configuration
└── README.md            # This file
```

Now you can check if the files were created using the correct PowerShell command:

```powershell
Get-ChildItem frontend
```

You should now see all the files including `package.json`, `pages/index.tsx`, etc. Then you can run:

```powershell
npm install
npm run dev
```

The files should now actually exist and the application should work properly!

## Technologies Used

- **Next.js 14** - React framework optimized for Vercel
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons

## Development Commands

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Deployment

This frontend is designed to work with Vercel deployment. The `next.config.js` includes proxy configuration for local development, but in production, you'll need to update the API URL to point to your deployed backend.

## Troubleshooting

- **API Connection Issues**: Ensure the FastAPI backend is running on port 8000
- **CORS Errors**: The backend includes CORS middleware to allow frontend requests
- **API Key Issues**: Make sure you have a valid OpenAI API key with sufficient credits
- **Build Issues**: Run `npm install` to ensure all dependencies are installed

## Design Principles

Following the frontend rules:
- ✅ Visual clarity and contrast (dark text on light backgrounds)
- ✅ Pleasant UX with proper content fitting
- ✅ Password-style input for sensitive API key information
- ✅ Next.js for optimal Vercel deployment
- ✅ Local testing capability
- ✅ Clear instructions for running the UI
