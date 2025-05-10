import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import Header from './components/Header';
import About from './components/About';
import ToolBar from './components/ToolBar';
import CodeEditor from './components/CodeEditor';

const App = () => {
    const [result, setResult] = useState(`// Start coding here\nfunction helloWorld() {\n    console.log("Hello, World!");\n}`);
    const [language, setLanguage] = useState('cpp');
    const [showAlert, setShowAlert] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => {
            setShowAlert(true);
        }, 3000);
        return () => clearTimeout(timer);
    }, []);

    const handleCloseAlert = () => {
        setShowAlert(false);
    };

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
        >
            {showAlert && (
                <Box
                    sx={{
                        position: 'fixed',
                        top: '10px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        backgroundColor: '#ff4444',
                        color: 'white',
                        padding: '8px 16px',
                        borderRadius: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        zIndex: 1000,
                        boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
                        maxWidth: '400px',
                        width: 'auto',
                        border: '2px solid #cc0000'
                    }}
                >
                    <span style={{ fontWeight: 'bold' }}>
                      ⚠️ Resource limits in effect, so responses may be delayed by up to 80 seconds.
                    </span>
                    <span 
                        onClick={handleCloseAlert}
                        style={{
                            cursor: 'pointer',
                            paddingLeft: '10px',
                            fontSize: '1.2rem',
                            fontWeight: 'bold',
                            color: 'white',
                            '&:hover': {
                                color: '#ffcccc'
                            }
                        }}
                    >
                        ×
                    </span>
                </Box>
            )}

            <div style={{ display: 'flex' }}>
                <Header />
                <About />
            </div>

            <ToolBar 
                result={result} 
                setResult={setResult} 
                setLanguage={setLanguage} 
            />
            
            <CodeEditor result={result} language={language} />
        </Box>
    );
};

export default App;