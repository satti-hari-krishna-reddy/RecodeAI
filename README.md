# Recode AI: Turning Complexity Into Clarity

Recode AI is a decompilation and analysis tool designed for developers, educators, cybersecurity experts, and enthusiasts. It leverages powerful Azure services and Ghidra to provide seamless binary decompilation, AI insights, and multi-language translation, all within a scalable and cost-effective serverless architecture.

## Problem We Solved
Binary files often contain valuable information that developers and security analysts need to retrieve, analyze, or modify, but decompiled binary files are notoriously cryptic and difficult to interpret. Variables lack meaningful names, logic is convoluted, and understanding the code often feels like deciphering a foreign language. This complexity slows down even the most seasoned experts and creates a significant barrier for newcomers.

**Recode AI** revolutionizes this process by leveraging AI to produce human-readable, well-documented source code from raw binaries. Whether you're:
- Analyzing legacy systems
- Investigating malware
- Gaining insights into unknown software

Recode AI simplifies the process, making it accessible and efficient for everyone.

## Features
- **AI-Augmented Decompilation**: Converts cryptic decompiled binaries into clean, understandable source code enriched with AI-generated comments.
- **Multi-Language Translation**: Translate decompiled code into your preferred programming language.
- **Rapid Analysis**: Ideal for experts who want to enhance their speed and accuracy.
- **Beginner-Friendly Insights**: Provides context and clarity for those new to reverse engineering.

## Workflow
1. **Upload Your Binary**: Users upload .exe or .out files via the intuitive frontend.
2. **Trigger Serverless Azure Function**: The binary is stored in Azure Blob Storage.
3. **Run Ghidra in a Container**: Azure Container Instances (ACI) deploy a containerized Ghidra instance, paired with a lightweight Go server, to decompile the binary.
4. **AI Enhancements**: AI processes the decompiled code, generating meaningful variable names, logical structures, and comments.
5. **Retrieve Results**: The enriched source code is saved back to Azure Blob Storage and sent to the user.

## Why Azure?
- **Scalability**: Azure Container Instances (ACI) allow us to run Ghidra on demand, scaling automatically with workload.
- **Serverless Efficiency**: Azure Functions handle the workflow seamlessly, minimizing operational overhead and costs.
- **Integration**: Azure Blob Storage ensures secure, efficient file handling throughout the process.

By utilizing Azure to its fullest, Recode AI provides a cost-effective, high-performing, and scalable solution. The seamless integration of these services underscores the complexity and innovation behind our platform.

## Tech Stack
- **Frontend**: React, JavaScript, Vite.
- **Backend**: Golang, Python, Ghidra (for decompiling the binaries), Docker.
- **AI**: Github Copilot, AI-based insights for code transformation.
- **Cloud Services**:  
  - Azure Functions
  - Azure Container Instances (ACI)
  - Azure Blob Storage

## Testing Instructions for the Judges

### Instructions to Run RecodeAI Locally

1. Update the `.env` file:  
   Replace the following placeholder with your GPT API key:  
   ```
   API_KEY=<your GEMINI API key>
   ```

2. Clone the repository:  
   ```bash
   git clone https://github.com/satti-hari-krishna-reddy/RecodeAI
   ```

3. Navigate to the project directory and start the services:  
   ```bash
   docker-compose up -d
   ```

4. Open your browser and visit:  
   ```
   http://localhost:5173
   ```

## Project Directory Explanation

- **`/ghidra_azure`**: Contains the backend code deployed as Azure Functions for cloud processing.
- **`/ghidra_local`**: Backend code that runs locally on the user’s machine without relying on cloud infrastructure.
- **`/RecodeUi`**: Frontend interface allowing users to interact with RecodeAI.

## Impact

### Developer Community
Recode AI accelerates workflows, reduces errors, and empowers developers to work smarter, not harder. Experts can dissect binaries faster, while beginners gain a tool that makes reverse engineering approachable.

### Beyond the Developer Community
The ability to decode and analyze binaries has implications for:
- **Cybersecurity**: Faster malware analysis to mitigate threats.
- **Education**: Tools for teaching reverse engineering to the next generation of developers.
- **Legacy Software**: Breathing new life into outdated systems.
