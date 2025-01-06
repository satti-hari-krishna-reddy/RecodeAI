package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gorilla/mux"
	"github.com/rs/cors"
)

const (
	ghidraSupportDir = "/app/ghidra_10.1_PUBLIC/support"
	scriptPath       = "/app/ghidra-headless"
	decompiledOutput = "/app/ghidra_10.1_PUBLIC/support/decompiled_output.c"
	defaultFileName  = "uploaded_binary.exe"
)

func setupCors() *cors.Cors {
	// Configure CORS options to allow all origins, methods, and headers
	return cors.New(cors.Options{
		AllowedOrigins: []string{"*"}, 
		AllowedMethods: []string{"GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"},
		AllowedHeaders: []string{"*"}, 
	})
}



func handleError(msg string, err error) {
	if err != nil {
		log.Printf("%s: %v", msg, err)
	}
}

func sanitizeFileName(fileName string) string {
	if strings.HasSuffix(fileName, ".exe") {
		return strings.TrimSuffix(fileName, ".exe")
	}
	return fileName
}

func saveUploadedFile(file multipart.File, handler *multipart.FileHeader) string {
	fileName := handler.Filename
	if fileName == "" {
		fileName = defaultFileName
	}

	sanitizedFileName := sanitizeFileName(fileName)
	binaryPath := filepath.Join("/app/binary", sanitizedFileName+".exe")

	out, err := os.Create(binaryPath)
	handleError("Failed to create file for uploaded binary", err)
	defer out.Close()

	_, err = io.Copy(out, file)
	handleError("Failed to save uploaded file", err)

	return binaryPath
}

func decompileBinary(binaryPath string) {
	log.Printf("Starting decompilation for: %s", binaryPath)
	cmd := exec.Command(
		"./analyzeHeadless",
		"/app/MyProjDir", "Myproj",
		"-import", binaryPath,
		"-scriptPath", scriptPath,
		"-postscript", "decompile_simple.py",
	)
	cmd.Dir = ghidraSupportDir

	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Decompilation failed: %v\nOutput: %s", err, string(output))
	}
	log.Printf("Decompilation completed. Output: %s", string(output))
}

func getDecompiledOutput() string {
	data, err := os.ReadFile(decompiledOutput)
	handleError("Failed to read decompiled file", err)
	return string(data)
}

func decompileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Only POST method is allowed", http.StatusMethodNotAllowed)
		return
	}

	r.ParseMultipartForm(10 << 20) // 10 MB limit
	file, handler, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Failed to parse file from request", http.StatusBadRequest)
		return
	}
	defer file.Close()

	binaryPath := saveUploadedFile(file, handler)
	decompileBinary(binaryPath)

	decompiledCode := getDecompiledOutput()

	Prompt := "Generate a **function relationship map** for the given code with: \n 1. Function Name \n2. Variables: List with brief roles. \n 3. Return Value: What it returns and why. \n 4. Relationships:  Variable/function interactions (e.g., calls, return usage). \n **Rules**: No code modifications. \n then give some space in the bottom and in the next follow this by adding  inline comments or documentation for the following code. The comments should describe the purpose of each block of code or important lines. Do not modify the original structure or indentation of the code in any way. The goal is to improve understanding without altering the actual code.Please focus only on the code without any commentary "
    aiInput := Prompt + "\n" + string(decompiledCode)
	aiResponse, err := InvokeAi(aiInput)
	
	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(aiResponse))	
}

func InvokeAi(prompt string) (string, error) {
	apiKey := os.Getenv("API_KEY")
	url := fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=%s", apiKey)

	// Request payload
	payload := map[string]interface{}{
		"contents": []map[string]interface{}{
			{
				"parts": []map[string]string{
					{"text": prompt},
				},
			},
		},
	}
	requestBody, err := json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request payload: %v", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
	if err != nil {
		return "", fmt.Errorf("failed to create request: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("request failed: %v", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response body: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API error: %s", body)
	}

	var result struct {
		Candidates []struct {
			Content struct {
				Parts []struct {
					Text string `json:"text"`
				} `json:"parts"`
			} `json:"content"`
		} `json:"candidates"`
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return "", fmt.Errorf("failed to unmarshal response: %v", err)
	}

	if len(result.Candidates) > 0 && len(result.Candidates[0].Content.Parts) > 0 {
		return result.Candidates[0].Content.Parts[0].Text, nil
	}

	return "", fmt.Errorf("no content found in the response")
}

func TranslationHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Ensure the Content-Type is text/plain
	if r.Header.Get("Content-Type") != "text/plain" {
		http.Error(w, "Invalid Content-Type, expected text/plain", http.StatusBadRequest)
		return
	}

	// Read the body as plain text
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusInternalServerError)
		return
	}

	// Attempt to parse the stringified JSON
	var requestBody struct {
		PseudoCode string `json:"pseudo_code"`
		Method     string `json:"method"`
		Lang       string `json:"lang"`
	}

	if err := json.Unmarshal(body, &requestBody); err != nil {
		http.Error(w, "Invalid JSON format in body", http.StatusBadRequest)
		return
	}

	// Validate required fields
	if requestBody.PseudoCode == "" || requestBody.Method == "" {
		http.Error(w, "Missing required fields: pseudo_code or method", http.StatusBadRequest)
		return
	}

	var prompt string
	switch requestBody.Method {
	case "recode":
		prompt = "Reconstruct the following code while maintaining its original logic. " +
			"The goal is to improve its readability, structure, and clarity, as though it were written from scratch in a cleaner and more modern style. " +
			"Do not alter the core logic of the code, only refactor the way it is written without commentary."
	case "translate":
		if requestBody.Lang == "" {
			http.Error(w, "Missing required field: lang for translation method", http.StatusBadRequest)
			return
		}
		prompt = "Translate the following code into " + requestBody.Lang + ". " +
			"Ensure that the logic remains exactly the same and that the translated code adheres to the syntax and conventions of the target language."
	default:
		http.Error(w, "Invalid method", http.StatusBadRequest)
		return
	}

	aiInput := prompt + "\n" + requestBody.PseudoCode

	aiResponse, _ := InvokeAi(aiInput)

	// Respond with plain text
	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(aiResponse))
}


func main() {
	// Create the router
	r := mux.NewRouter()

	// Register your routes
	r.HandleFunc("/decompile", decompileHandler).Methods(http.MethodPost)
	r.HandleFunc("/translate", TranslationHandler).Methods(http.MethodPost)

	// Set up CORS
	corsHandler := setupCors()

	// Start the server with CORS middleware applied
	log.Printf("Starting server on port 5000...")
	log.Fatal(http.ListenAndServe(":5000", corsHandler.Handler(r)))
}
