import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, Box, Typography } from '@mui/material';
import ChatInterface from './components/ChatInterface';
import rtlPlugin from 'stylis-plugin-rtl';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { prefixer } from 'stylis';

// Create RTL cache
const cacheRtl = createCache({
  key: 'muirtl',
  stylisPlugins: [prefixer, rtlPlugin],
});

// Create RTL theme
const theme = createTheme({
  direction: 'rtl',
  typography: {
    fontFamily: 'Arial, sans-serif',
  },
  palette: {
    primary: {
      main: '#27ae60',
    },
    secondary: {
      main: '#2c3e50',
    },
  },
});

const App: React.FC = () => {
  return (
    <CacheProvider value={cacheRtl}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth="md">
          <Box sx={{ my: 4, textAlign: 'center' }}>
            <Typography variant="h3" component="h1" gutterBottom>
              المساعد العربي
            </Typography>
            <Typography variant="h6" color="text.secondary" paragraph>
              مرحباً بك في المساعد العربي. يمكنك طرح أسئلتك كتابةً أو باستخدام الميكروفون.
            </Typography>
          </Box>
          <ChatInterface />
        </Container>
      </ThemeProvider>
    </CacheProvider>
  );
};

export default App; 