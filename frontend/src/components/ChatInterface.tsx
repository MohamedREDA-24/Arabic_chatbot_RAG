import React, { useState, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Mic, Send, ThumbUp, ThumbDown } from '@mui/icons-material';
import axios from 'axios';

interface ChatMessage {
  query: string;
  answer: string;
  feedback?: boolean;
  comment?: string;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [feedbackDialog, setFeedbackDialog] = useState<{
    open: boolean;
    messageIndex: number;
  }>({ open: false, messageIndex: -1 });
  const [feedbackComment, setFeedbackComment] = useState('');

  const recognitionRef = useRef<any>(null);

  const startListening = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.lang = 'ar-SA';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsListening(false);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } else {
      alert('Speech recognition is not supported in your browser.');
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    try {
      const response = await axios.post(`${API_URL}/query`, {
        query: input,
      });

      setMessages([
        {
          query: input,
          answer: response.data.answer,
        },
        ...messages,
      ]);
      setInput('');
    } catch (error) {
      console.error('Error sending message:', error);
      alert('حدث خطأ في الاتصال');
    }
  };

  const handleFeedback = async (messageIndex: number, isPositive: boolean) => {
    if (isPositive) {
      try {
        await axios.post(`${API_URL}/feedback`, {
          query: messages[messageIndex].query,
          answer: messages[messageIndex].answer,
          feedback: true,
        });
        alert('شكراً على تقييمك الإيجابي!');
      } catch (error) {
        console.error('Error sending feedback:', error);
        alert('حدث خطأ في إرسال التقييم');
      }
    } else {
      setFeedbackDialog({ open: true, messageIndex });
    }
  };

  const handleFeedbackSubmit = async () => {
    try {
      await axios.post(`${API_URL}/feedback`, {
        query: messages[feedbackDialog.messageIndex].query,
        answer: messages[feedbackDialog.messageIndex].answer,
        feedback: false,
        comment: feedbackComment,
      });
      alert('شكراً على ملاحظاتك! سنعمل على تحسين الإجابة.');
      setFeedbackDialog({ open: false, messageIndex: -1 });
      setFeedbackComment('');
    } catch (error) {
      console.error('Error sending feedback:', error);
      alert('حدث خطأ في إرسال التقييم');
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2 }}>
        {messages.map((message, index) => (
          <Paper
            key={index}
            elevation={2}
            sx={{
              p: 2,
              mb: 2,
              backgroundColor: '#f8f9fa',
              borderRadius: 2,
            }}
          >
            <Typography
              variant="h6"
              color="secondary"
              sx={{ mb: 1, borderRight: '3px solid #2c3e50', pr: 1 }}
            >
              السؤال: {message.query}
            </Typography>
            <Typography
              variant="body1"
              color="primary"
              sx={{ mb: 2, borderRight: '3px solid #27ae60', pr: 1 }}
            >
              الإجابة: {message.answer}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton
                color="primary"
                onClick={() => handleFeedback(index, true)}
              >
                <ThumbUp />
              </IconButton>
              <IconButton
                color="error"
                onClick={() => handleFeedback(index, false)}
              >
                <ThumbDown />
              </IconButton>
            </Box>
          </Paper>
        ))}
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="اكتب سؤالك هنا..."
          variant="outlined"
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <IconButton
          color={isListening ? 'error' : 'primary'}
          onClick={startListening}
          disabled={isListening}
        >
          <Mic />
        </IconButton>
        <IconButton color="primary" onClick={handleSend}>
          <Send />
        </IconButton>
      </Box>

      <Dialog open={feedbackDialog.open} onClose={() => setFeedbackDialog({ open: false, messageIndex: -1 })}>
        <DialogTitle>ملاحظاتك</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={feedbackComment}
            onChange={(e) => setFeedbackComment(e.target.value)}
            placeholder="يرجى كتابة ملاحظاتك لتحسين الإجابة..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialog({ open: false, messageIndex: -1 })}>
            إلغاء
          </Button>
          <Button onClick={handleFeedbackSubmit} color="primary">
            إرسال
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatInterface; 