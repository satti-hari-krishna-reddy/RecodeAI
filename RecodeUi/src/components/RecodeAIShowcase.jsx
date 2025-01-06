import React from 'react';
import { Box, Typography } from '@mui/material';
import { styled } from '@mui/system';
import MonacoEditor from '@monaco-editor/react';

const GradientBackground = styled(Box)({
  background: 'linear-gradient(135deg, #ff9a9e 0%, #fad0c4 99%, #fad0c4 100%)',
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  zIndex: -1,
  filter: 'blur(20px)',
});

const DisplayContainer = styled(Box)({
  position: 'relative',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  borderRadius: '12px',
  backdropFilter: 'blur(20px)',
  backgroundColor: 'rgba(255, 255, 255, 0.15)',
  boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.1)',
  maxWidth: '800px',
  margin: 'auto',
  '@media (min-width: 768px)': {
    flexDirection: 'row',
  },
});

const InfoContainer = styled(Box)({
  textAlign: 'center',
  maxWidth: '100%',
  padding: '8px', // Reduced padding
  '@media (min-width: 768px)': {
    maxWidth: '50%',
    textAlign: 'left',
    paddingRight: '8px',
  },
});

const InfoTitle = styled(Typography)({
  color: '#ffffff',
  fontSize: '1.8rem', // Slightly smaller for compactness
  fontWeight: 'bold',
  textShadow: '1px 1px 4px rgba(0, 0, 0, 0.4)', // Subtle shadow
  '@media (min-width: 768px)': {
    fontSize: '2.2rem',
  },
});

const InfoDescription = styled(Typography)({
  color: '#ffffff',
  marginTop: '8px', // Reduced top margin
  fontSize: '0.9rem', // Reduced font size
  lineHeight: 1.6, // Compact line height
  '@media (min-width: 768px)': {
    fontSize: '1.1rem',
  },
});


const CodeEditor = () => {
  return (
    <div
      style={{
        width: '100%',
        height: '300px', // Fixed height for demo purposes
        borderRadius: '10px',
        overflow: 'hidden',
        background: '#1E1E1E',
      }}
    >
      <MonacoEditor
        height="100%"
        defaultLanguage="javascript"
        defaultValue={`// Start coding here\nfunction helloWorld() {\n    console.log("Hello, World!");\n}`}
        theme="vs-dark"
        options={{
          fontSize: 16,
          fontFamily: 'Fira Code, monospace',
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          smoothScrolling: true,
          automaticLayout: true,
          wordWrap: 'on',
        }}
      />
    </div>
  );
};

const RecodeAIShowcase = () => {
  return (
    <Box
      sx={{
        position: 'relative',
        overflow: 'hidden',
        padding: '16px',
      }}
    >
      <GradientBackground />
      <DisplayContainer>
        <InfoContainer>
          <InfoTitle>How Recode AI Works</InfoTitle>
          <InfoDescription>
            Upload your binary file, decompile it with a single click, and explore AI-generated insights on the source code.
            Effortlessly translate and rebuild decompiled code in various languages for analysis or modification.
          </InfoDescription>
        </InfoContainer>
        {/* <CodeEditor /> */}
      </DisplayContainer>
    </Box>
  );
};

export default RecodeAIShowcase;
