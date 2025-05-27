# Arabic Chatbot Frontend

This is the React frontend for the Arabic Legal Chatbot application.

## Features

- RTL (Right-to-Left) support for Arabic text
- Voice input using browser's speech recognition
- Chat interface with message history
- Feedback system with thumbs up/down
- Modern Material-UI design

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the root directory with the following content:
```
REACT_APP_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm start
```

## Dependencies

- React 18
- TypeScript
- Material-UI
- Axios
- Emotion (for styling)

## Browser Support

The application uses the Web Speech API for voice input, which is supported in:
- Chrome
- Edge
- Safari
- Firefox (with limited support)

## Development

The application is built with:
- TypeScript for type safety
- Material-UI for components and styling
- Emotion for CSS-in-JS
- Axios for API calls

## Building for Production

To create a production build:

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory. 