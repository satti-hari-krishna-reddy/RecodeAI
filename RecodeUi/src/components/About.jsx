import React from 'react';
import { Box, Typography } from '@mui/material';

const About = () => {
    return (
        <Box sx={{
            padding: '40px 20px',
            maxWidth: '800px',
            margin: 'auto',
            textAlign: 'center',
            backgroundColor: '#000', // Pure black background
            borderRadius: '10px',
            boxShadow: '0 4px 10px rgba(255, 255, 255, 0.1)' // Subtle glow for contrast
        }}>
            <Typography variant="h3" sx={{
                fontWeight: 'bold',
                background: 'linear-gradient(45deg, #00FFA3, #DC1FFF)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                marginBottom: '20px'
            }}>
                Recode AI: Turning Complexity Into Clarity
            </Typography>

            <Typography variant="h5" sx={{
                marginBottom: '20px',
                color: '#E5E5E5' // Light gray for readability
            }}>
                What if understanding binary files was as easy as reading a book? Welcome to Recode AI—the future of reverse engineering.
            </Typography>

            <Typography variant="body1" sx={{
                marginBottom: '20px',
                lineHeight: '1.6',
                fontSize: '1.2rem',
                color: '#CCCCCC' // Softer gray for contrast against the background
            }}>
                Decompilation just got an upgrade. With the power of AI, Recode AI transforms raw binary into clean, human-readable code that evolves with you. Designed for developers, educators, and cybersecurity experts, this is your gateway to decoding the unknown.
            </Typography>

            <Box sx={{
                padding: '20px',
                background: '#212121', // Subtle dark gray gradient for section highlight
                borderRadius: '10px',
                marginBottom: '20px'
            }}>
                <Typography variant="h6" sx={{
                    fontWeight: 'bold',
                    color: '#FFFFFF', // Pure white for emphasis
                    marginBottom: '10px'
                }}>
                    From Assembly to Insight in a Blink
                </Typography>
                <Typography variant="body1" sx={{
                    lineHeight: '1.6',
                    fontSize: '1.1rem',
                    color: '#AAAAAA' // Soft gray for body text
                }}>
                    Upload. Decode. Rebuild. Recode AI takes your binaries and reconstructs them into functional, well-documented source code. Every line is enriched with AI-generated comments and context, making even the most complex software easy to understand.
                </Typography>
            </Box>

            <Typography variant="body1" sx={{
                lineHeight: '1.6',
                fontSize: '1.2rem',
                color: '#E5E5E5' // Light gray for contrast
            }}>
                Whether you’re analyzing legacy systems, dissecting malware, or simply curious about what lies beneath the surface, <strong>Recode AI gives you superpowers.</strong>
            </Typography>
        </Box>
    );
};

export default About;
