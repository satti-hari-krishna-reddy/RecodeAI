import React, { useRef } from 'react';
import MonacoEditor from '@monaco-editor/react';
import { IconButton, Tooltip } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

const CodeEditor = ({result, language}) => {
  const editorRef = useRef(null);

  const handleCopy = () => {
    const code = editorRef.current?.getValue(); 
    if (code) {
      navigator.clipboard.writeText(code);
      alert("Code copied to clipboard!");
    }
  };

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor; 
  };

  return (
    <div
      style={{
        width: '60%',
        maxHeight: '700px',
        height: '500px',
        borderRadius: '10px',
        overflow: 'hidden',
        background: '#1E1E1E',
        padding: '15px',
        margin: '20px auto',
        position: 'relative', 
      }}
    >
      <Tooltip title="Copy Code">
        <IconButton
          onClick={handleCopy}
          sx={{
            position: 'absolute',
            top: '10px',
            right: '15px',
            zIndex: 1, 
            color: 'white',
            background: 'rgba(0, 0, 0, 0.5)',
            borderRadius: '50%',
            '&:hover': {
              background: 'rgba(255, 255, 255, 0.2)',
            },
          }}
        >
          <ContentCopyIcon />
        </IconButton>
      </Tooltip>

      <MonacoEditor
        height="100%"
        defaultLanguage={language}
        defaultValue={result}
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
        onMount={handleEditorDidMount} 
      />
    </div>
  );
};

export default CodeEditor;
