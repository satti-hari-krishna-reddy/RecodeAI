package main

import (
	"bytes"
	"context"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
)

const (
	ghidraSupportDir  = "/app/ghidra_10.1_PUBLIC/support"
	scriptPath        = "/app/ghidra-headless"
	decompiledOutput  = "/app/ghidra_10.1_PUBLIC/support/decompiled_output.c"
	binariesContainer = "binaries"
)

func handleError(msg string, err error) {
	if err != nil {
		log.Fatalf("%s: %v", msg, err)
	}
}

func sanitizeFileName(blobName string) string {
	if strings.HasSuffix(blobName, ".exe") {
		return strings.TrimSuffix(blobName, ".exe")
	}
	return blobName
}

func downloadBlob(ctx context.Context, containerName, blobName string) string {
	connectionString := os.Getenv("CONNECTION_STRING")
	client, err := azblob.NewClientFromConnectionString(connectionString, nil)
	handleError("Failed to create Azure Blob client", err)

	log.Printf("Downloading blob: %s from container: %s", blobName, containerName)
	get, err := client.DownloadStream(ctx, containerName, blobName, nil)
	handleError("Failed to download blob", err)

	// Read the downloaded data
	downloadedData := bytes.Buffer{}
	retryReader := get.NewRetryReader(ctx, &azblob.RetryReaderOptions{})
	_, err = downloadedData.ReadFrom(retryReader)
	handleError("Failed to read blob stream", err)
	defer retryReader.Close()

	// Reconstruct the file name
	sanitizedFileName := sanitizeFileName(blobName)
	binaryPath := filepath.Join("/app/binary", sanitizedFileName+".exe")

	err = ioutil.WriteFile(binaryPath, downloadedData.Bytes(), 0644)
	handleError("Failed to save the downloaded file", err)

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
		log.Fatalf("Decompilation failed: %v\nOutput: %s", err, string(output))
	}
	log.Printf("Decompilation completed. Output: %s", string(output))
}

func uploadDecompiledFile(ctx context.Context, originalFileName string) {
	connectionString := os.Getenv("CONNECTION_STRING")
	client, err := azblob.NewClientFromConnectionString(connectionString, nil)
	handleError("Failed to create Azure Blob client", err)

	data, err := ioutil.ReadFile(decompiledOutput)
	handleError("Failed to read decompiled file", err)

	sanitizedFileName := sanitizeFileName(originalFileName)
	finalFileName := sanitizedFileName + ".c"
	containerName := os.Getenv("AZURE_CONTAINER_NAME")

	log.Printf("Uploading decompiled file: %s", finalFileName)
	_, err = client.UploadBuffer(ctx, containerName, finalFileName, data, &azblob.UploadBufferOptions{})
	handleError("Failed to upload decompiled file", err)

	log.Printf("Decompiled file uploaded successfully as: %s", finalFileName)
}

func main() {
	log.Printf("Starting decompilation process...")

	blobName := os.Getenv("BLOB_NAME")
	if blobName == "" {
		log.Printf("Environment variable BLOB_NAME is required")
	}

	ctx := context.Background()

	binaryPath := downloadBlob(ctx, binariesContainer, blobName)
	decompileBinary(binaryPath)
	uploadDecompiledFile(ctx, filepath.Base(binaryPath))

	// Exit the program
	log.Printf("Decompilation process completed. Exiting...")
	os.Exit(0)
}
