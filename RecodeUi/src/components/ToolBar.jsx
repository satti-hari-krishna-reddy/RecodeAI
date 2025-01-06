import React, { useState } from 'react';
import { AppBar, Toolbar, Button, Menu, MenuItem, CircularProgress, Snackbar, Alert } from '@mui/material';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';

const ToolBar = ({ result, setResult, setLanguage, isCodeEditorVisible }) => {
    const [demoAnchorEl, setDemoAnchorEl] = useState(null);
    const [translateAnchorEl, setTranslateAnchorEl] = useState(null);
    const [activeButton, setActiveButton] = useState('');
    const [demoButtonText, setDemoButtonText] = useState('Demo Executables');
    const [translateButtonText, setTranslateButtonText] = useState('Translate');
    const [uploadButtonText, setUploadButtonText] = useState('Upload Executable');
    const [showSnackbar, setShowSnackbar] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');
    const [isLoading, setIsLoading] = useState({ decode: false, recode: false, translate: false });
    const [uploadedFile, setUploadedFile] = useState(null);

    const MAX_FILE_SIZE_MB = 5; // Maximum file size in MB
    const backendUrl = import.meta.env.VITE_BACKEND_URL;

    const handleDemoClick = (event) => setDemoAnchorEl(event.currentTarget);
    const handleDemoClose = (option) => {
        setDemoAnchorEl(null);
        if (option) {
            setDemoButtonText(option);
            setUploadedFile(option); 
        }
    };

    const handleTranslateClick = (event) => setTranslateAnchorEl(event.currentTarget);
    const handleTranslateClose = async (option) => {
        setTranslateAnchorEl(null);
        if (option) {
            setTranslateButtonText(option);
            setLanguage(option);
            if (!result) {
                showSnackbarMessage('No pseudo-code available to translate.');
                return;
            }
            setIsLoading((prev) => ({ ...prev, translate: true }));
            try {
                const response = await fetch(backendUrl + '/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pseudo_code: result,
                        method: 'translate',
                        lang: option,
                    }),
                });
                const data = await response.json();
                setResult(data.translatedCode || 'Translation completed.');
            } catch (error) {
                showSnackbarMessage('Translation failed. Please try again.');
            } finally {
                setIsLoading((prev) => ({ ...prev, translate: false }));
            }
        }
    };


    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const fileExtension = file.name.split('.').pop().toLowerCase();
        const validExtensions = ['exe', 'out'];
        if (!validExtensions.includes(fileExtension)) {
            showSnackbarMessage('Invalid file type. Only .exe or .out files are allowed.');
            return;
        }

        const fileSizeMB = file.size / (1024 * 1024);
        if (fileSizeMB > MAX_FILE_SIZE_MB) {
            showSnackbarMessage(`File size exceeds ${MAX_FILE_SIZE_MB} MB limit.`);
            return;
        }

        setUploadButtonText(file.name);
        setUploadedFile(file);
        showSnackbarMessage(`File "${file.name}" uploaded successfully.`);
    };

    const handleMockApiCall = async (buttonKey) => {
        if (buttonKey === 'decode' && !uploadedFile) {
            showSnackbarMessage('Please upload a file or select a demo executable before decoding.');
            return;
        }

        setIsLoading((prev) => ({ ...prev, [buttonKey]: true }));
        try {
            const url =
                buttonKey === 'decode'
                    ? backendUrl + '/decompile'
                    : backendUrl + '/translate';

            const body =
                buttonKey === 'decode'
                    ? uploadedFile
                    : JSON.stringify({
                          pseudo_code: result,
                          method: 'recode',
                          lang: 'N/A',
                      });

            const headers = buttonKey === 'decode' ? {} : { 'Content-Type': 'application/json' };
            const options = {
                method: 'POST',
                headers,
                body: buttonKey === 'decode' ? body : JSON.stringify(body),
            };

            const response = await fetch(url, options);
            const data = await response.json();

            if (buttonKey === 'decode') {
                setResult(data.decompiledCode || 'Decoding completed.');
            } else {
                setResult(data.reconstructedCode || 'Recode completed.');
            }
        } catch (error) {
            showSnackbarMessage(`${buttonKey === 'decode' ? 'Decoding' : 'Recode'} failed. Please try again.`);
        } finally {
            setIsLoading((prev) => ({ ...prev, [buttonKey]: false }));
        }
    };

    const showSnackbarMessage = (message) => {
        setSnackbarMessage(message);
        setShowSnackbar(true);
    };

    const buttonStyle = {
        color: '#fff',
        fontWeight: 'bold',
        borderRadius: '20px',
        padding: '10px 20px',
        textTransform: 'none',
        boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',
        transition: 'transform 0.2s ease-in-out',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        '&:hover': {
            transform: 'scale(1.05)',
        },
    };

    const menuStyle = {
        fontFamily: 'Poppins, sans-serif',
        fontSize: '14px',
        padding: '8px 16px',
    };

    return (
        <AppBar
            position="sticky"
            sx={{
                background: 'rgba(255, 255, 255, 0.3)',
                backdropFilter: 'blur(10px)',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
                borderBottom: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '25px',
                height: 'fit-content',
                width: 'fit-content',
                margin: '20px auto',
            }}
        >
            <Toolbar sx={{ display: 'flex', gap: '15px' }}>
                {/* Upload Executable Button */}
                <Button
                    component="label"
                    sx={{
                        ...buttonStyle,
                        backgroundColor: '#DC1FFF',
                        '&:hover': { backgroundColor: '#00FFA3' },
                    }}
                >
                    {uploadButtonText}
                    <input
                        type="file"
                        hidden
                        onChange={handleFileUpload}
                        accept=".exe,.out"
                    />
                </Button>

                {/* Demo Executables Dropdown */}
                <Button
                    sx={{
                        ...buttonStyle,
                        backgroundColor: '#FF5722',
                        '&:hover': { backgroundColor: '#E64A19' },
                    }}
                    onClick={handleDemoClick}
                >
                    {demoButtonText} <ArrowDropDownIcon sx={{ marginLeft: '5px' }} />
                </Button>
                <Menu
                    anchorEl={demoAnchorEl}
                    open={Boolean(demoAnchorEl)}
                    onClose={() => handleDemoClose()}
                    sx={{ '& .MuiPaper-root': { borderRadius: '15px', padding: '5px 0' } }}
                >
                    <MenuItem sx={menuStyle} onClick={() => handleDemoClose('prime_numbers.exe')}>
                        prime_numbers.exe
                    </MenuItem>
                </Menu>

                {/* Decode Button */}
                <Button
                    sx={{
                        ...buttonStyle,
                        backgroundColor: '#007BFF',
                        '&:hover': { backgroundColor: '#0056B3' },
                    }}
                    onClick={() => handleMockApiCall('decode')}
                >
                    {isLoading.decode ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : 'Decode'}
                </Button>

                {/* Recode Button */}
                <Button
                    sx={{
                        ...buttonStyle,
                        backgroundColor: 'transparent',
                        color: '#000',
                        borderBottom: activeButton === 'reconstruct' ? '2px solid #000' : 'none',
                        '&:hover': { color: '#555' },
                    }}
                    onClick={() => handleMockApiCall('recode')}
                >
                    {isLoading.recode ? <CircularProgress size={20} sx={{ color: '#000' }} /> : 'Recode'}
                </Button>

                {/* Translate Dropdown */}
                <Button
                    sx={{
                        ...buttonStyle,
                        backgroundColor: '#4CAF50',
                        '&:hover': { backgroundColor: '#388E3C' },
                    }}
                    onClick={handleTranslateClick}
                >
                    {translateButtonText} <ArrowDropDownIcon sx={{ marginLeft: '5px' }} />
                </Button>
                <Menu
                    anchorEl={translateAnchorEl}
                    open={Boolean(translateAnchorEl)}
                    onClose={() => handleTranslateClose()}
                    sx={{ '& .MuiPaper-root': { borderRadius: '15px', padding: '5px 0' } }}
                >
                    <MenuItem sx={menuStyle} onClick={() => handleTranslateClose('Python')}>
                        Python
                    </MenuItem>
                    <MenuItem sx={menuStyle} onClick={() => handleTranslateClose('Java')}>
                        Java
                    </MenuItem>
                    <MenuItem sx={menuStyle} onClick={() => handleTranslateClose('C++')}>
                        C++
                    </MenuItem>
                    <MenuItem sx={menuStyle} onClick={() => handleTranslateClose('Golang')}>
                        Golang
                    </MenuItem>
                    <MenuItem sx={menuStyle} onClick={() => handleTranslateClose('JavaScript')}>
                        JavaScript
                    </MenuItem>
                </Menu>
            </Toolbar>

            {/* Snackbar for Popup */}
            <Snackbar
                open={showSnackbar}
                autoHideDuration={3000}
                onClose={() => setShowSnackbar(false)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert severity="success" sx={{ width: '100%' }}>
                    {snackbarMessage}
                </Alert>
            </Snackbar>
        </AppBar>
    );
};

export default ToolBar;
