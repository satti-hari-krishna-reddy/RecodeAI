import React from 'react';
import { useState } from 'react';
import { Box } from '@mui/material';
import Header from './components/Header';
import About from './components/About';
import ToolBar from './components/ToolBar';
import CodeEditor from './components/CodeEditor';

const App = () => {
    const [result, setResult] = useState(`// Start coding here\nfunction helloWorld() {\n    console.log("Hello, World!");\n}`);
    const [language, setLanguage] = useState('javascript');
    return (
<Box
    sx={{
        minHeight: '100vh',
        position: 'relative',
        overflow: 'hidden',
        color: 'white',
        padding: '20px',
        boxSizing: 'border-box',
        background: 'linear-gradient(135deg, #ffafbd, #ffc3a0, #d5aaff, #a0c4ff, #8ecae6)',
        backgroundSize: 'cover',
        backgroundPosition: 'center center',
    }}
>  <div style={{'display' : 'flex'}}>    <Header />
<About /></div>

<ToolBar setResult={setResult} setLanguage={setLanguage}/>
<CodeEditor result={result} language={language}/>
</Box>

    );
};

export default App;
