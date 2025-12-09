// Encypher CLI - Command-line tool for signing and verifying content
//
// Usage:
//
//	encypher sign --text "Hello, world!"
//	encypher verify --file signed.txt
//	encypher lookup <document_id>
//
// Environment:
//
//	ENCYPHER_API_KEY - Your API key (required)
//	ENCYPHER_BASE_URL - API base URL (default: https://api.encypherai.com)
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strings"
	"time"

	"github.com/spf13/cobra"

	encypher "github.com/encypherai/sdk-go"
)

var (
	// Global flags
	apiKey  string
	baseURL string
	timeout time.Duration
	output  string

	// Version info (set at build time)
	version = "dev"
	commit  = "none"
	date    = "unknown"
)

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

var rootCmd = &cobra.Command{
	Use:   "encypher",
	Short: "Encypher CLI - Sign and verify content with C2PA manifests",
	Long: `Encypher CLI provides command-line access to the Encypher Enterprise API
for signing content with C2PA manifests and verifying signed content.

Set your API key via ENCYPHER_API_KEY environment variable or --api-key flag.`,
	PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
		// Load API key from environment if not provided
		if apiKey == "" {
			apiKey = os.Getenv("ENCYPHER_API_KEY")
		}
		if apiKey == "" && cmd.Name() != "version" && cmd.Name() != "help" {
			return fmt.Errorf("API key required. Set ENCYPHER_API_KEY or use --api-key")
		}
		return nil
	},
}

var signCmd = &cobra.Command{
	Use:   "sign",
	Short: "Sign content with a C2PA manifest",
	Long: `Sign text content with a C2PA manifest embedding.

The signed content will include invisible Unicode characters that encode
the cryptographic signature and metadata.`,
	Example: `  # Sign text directly
  encypher sign --text "Hello, world!"

  # Sign from file
  encypher sign --file document.txt

  # Sign from stdin
  cat document.txt | encypher sign

  # Sign with title
  encypher sign --text "Content" --title "My Document"

  # Output to file
  encypher sign --file doc.txt --output signed.txt`,
	RunE: runSign,
}

var verifyCmd = &cobra.Command{
	Use:   "verify",
	Short: "Verify signed content",
	Long: `Verify content that was signed with a C2PA manifest.

Returns verification status, signer information, and manifest details.`,
	Example: `  # Verify text directly
  encypher verify --text "signed content..."

  # Verify from file
  encypher verify --file signed.txt

  # Verify from stdin
  cat signed.txt | encypher verify`,
	RunE: runVerify,
}

var lookupCmd = &cobra.Command{
	Use:   "lookup <document_id>",
	Short: "Look up a document by ID",
	Long:  `Retrieve information about a previously signed document using its document ID.`,
	Args:  cobra.ExactArgs(1),
	RunE:  runLookup,
}

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print version information",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("encypher %s\n", version)
		fmt.Printf("  commit: %s\n", commit)
		fmt.Printf("  built:  %s\n", date)
	},
}

// Sign command flags
var (
	signText   string
	signFile   string
	signTitle  string
	signOutput string
)

// Verify command flags
var (
	verifyText string
	verifyFile string
)

func init() {
	// Global flags
	rootCmd.PersistentFlags().StringVar(&apiKey, "api-key", "", "API key (or set ENCYPHER_API_KEY)")
	rootCmd.PersistentFlags().StringVar(&baseURL, "base-url", "https://api.encypherai.com", "API base URL")
	rootCmd.PersistentFlags().DurationVar(&timeout, "timeout", 30*time.Second, "Request timeout")
	rootCmd.PersistentFlags().StringVarP(&output, "output", "o", "", "Output format: json, text (default: text)")

	// Sign command flags
	signCmd.Flags().StringVarP(&signText, "text", "t", "", "Text to sign")
	signCmd.Flags().StringVarP(&signFile, "file", "f", "", "File to sign")
	signCmd.Flags().StringVar(&signTitle, "title", "", "Document title")
	signCmd.Flags().StringVarP(&signOutput, "output", "o", "", "Output file (default: stdout)")

	// Verify command flags
	verifyCmd.Flags().StringVarP(&verifyText, "text", "t", "", "Signed text to verify")
	verifyCmd.Flags().StringVarP(&verifyFile, "file", "f", "", "Signed file to verify")

	// Add commands
	rootCmd.AddCommand(signCmd)
	rootCmd.AddCommand(verifyCmd)
	rootCmd.AddCommand(lookupCmd)
	rootCmd.AddCommand(versionCmd)
}

func getInput(text, file string) (string, error) {
	if text != "" && file != "" {
		return "", fmt.Errorf("provide either --text or --file, not both")
	}

	if text != "" {
		return text, nil
	}

	if file != "" {
		data, err := os.ReadFile(file)
		if err != nil {
			return "", fmt.Errorf("failed to read file: %w", err)
		}
		return string(data), nil
	}

	// Try stdin
	stat, _ := os.Stdin.Stat()
	if (stat.Mode() & os.ModeCharDevice) == 0 {
		data, err := io.ReadAll(os.Stdin)
		if err != nil {
			return "", fmt.Errorf("failed to read stdin: %w", err)
		}
		return string(data), nil
	}

	return "", fmt.Errorf("no input provided. Use --text, --file, or pipe via stdin")
}

func runSign(cmd *cobra.Command, args []string) error {
	text, err := getInput(signText, signFile)
	if err != nil {
		return err
	}

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	// Create client and sign
	client := NewClient(apiKey, baseURL)
	result, err := client.Sign(ctx, text, signTitle)
	if err != nil {
		return fmt.Errorf("signing failed: %w", err)
	}

	// Output result
	if output == "json" {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		return enc.Encode(result)
	}

	// Text output
	if signOutput != "" {
		if err := os.WriteFile(signOutput, []byte(result.SignedText), 0644); err != nil {
			return fmt.Errorf("failed to write output: %w", err)
		}
		fmt.Fprintf(os.Stderr, "✓ Signed content written to %s\n", signOutput)
		fmt.Fprintf(os.Stderr, "  Document ID: %s\n", result.DocumentID)
	} else {
		fmt.Print(result.SignedText)
	}

	return nil
}

func runVerify(cmd *cobra.Command, args []string) error {
	text, err := getInput(verifyText, verifyFile)
	if err != nil {
		return err
	}

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	client := NewClient(apiKey, baseURL)
	result, err := client.Verify(ctx, text)
	if err != nil {
		return fmt.Errorf("verification failed: %w", err)
	}

	// Output result
	if output == "json" {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		return enc.Encode(result)
	}

	// Text output
	if result.Valid {
		fmt.Println("✓ Content is valid")
	} else {
		fmt.Println("✗ Content is invalid")
	}

	if result.SignerName != "" {
		fmt.Printf("  Signer: %s\n", result.SignerName)
	}
	if result.SignedAt != "" {
		fmt.Printf("  Signed: %s\n", result.SignedAt)
	}
	if result.DocumentID != "" {
		fmt.Printf("  Document ID: %s\n", result.DocumentID)
	}

	if !result.Valid {
		os.Exit(1)
	}
	return nil
}

func runLookup(cmd *cobra.Command, args []string) error {
	documentID := args[0]

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	client := NewClient(apiKey, baseURL)
	result, err := client.Lookup(ctx, documentID)
	if err != nil {
		return fmt.Errorf("lookup failed: %w", err)
	}

	// Output result
	if output == "json" {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		return enc.Encode(result)
	}

	// Text output
	fmt.Printf("Document: %s\n", documentID)
	if result.Title != "" {
		fmt.Printf("  Title: %s\n", result.Title)
	}
	if result.SignerName != "" {
		fmt.Printf("  Signer: %s\n", result.SignerName)
	}
	if result.CreatedAt != "" {
		fmt.Printf("  Created: %s\n", result.CreatedAt)
	}

	return nil
}

// Client wraps the Encypher API using the generated SDK
type Client struct {
	api *encypher.APIClient
}

// NewClient creates a new API client
func NewClient(apiKey, baseURL string) *Client {
	cfg := encypher.NewConfiguration()
	cfg.Servers = encypher.ServerConfigurations{{URL: strings.TrimSuffix(baseURL, "/")}}
	cfg.AddDefaultHeader("Authorization", "Bearer "+apiKey)

	return &Client{
		api: encypher.NewAPIClient(cfg),
	}
}

// SignResult represents the response from signing
type SignResult struct {
	SignedText string `json:"signed_text"`
	DocumentID string `json:"document_id"`
}

// VerifyResult represents the response from verification
type VerifyResult struct {
	Valid      bool   `json:"valid"`
	SignerName string `json:"signer_name,omitempty"`
	SignedAt   string `json:"signed_at,omitempty"`
	DocumentID string `json:"document_id,omitempty"`
	Message    string `json:"message,omitempty"`
}

// LookupResult represents the response from lookup
type LookupResult struct {
	DocumentID string `json:"document_id"`
	Title      string `json:"title,omitempty"`
	SignerName string `json:"signer_name,omitempty"`
	CreatedAt  string `json:"created_at,omitempty"`
}

// Sign signs content with a C2PA manifest
func (c *Client) Sign(ctx context.Context, text, title string) (*SignResult, error) {
	req := encypher.NewSignRequest(text)
	if title != "" {
		req.SetDocumentTitle(title)
	}

	resp, _, err := c.api.SigningAPI.SignContentApiV1SignPost(ctx).SignRequest(*req).Execute()
	if err != nil {
		return nil, err
	}

	return &SignResult{
		SignedText: resp.GetSignedText(),
		DocumentID: resp.GetDocumentId(),
	}, nil
}

// Verify verifies signed content
func (c *Client) Verify(ctx context.Context, text string) (*VerifyResult, error) {
	req := encypher.NewVerifyTextRequest(text)

	resp, _, err := c.api.VerificationAPI.VerifyTextApiV1VerifyPost(ctx).VerifyTextRequest(*req).Execute()
	if err != nil {
		return nil, err
	}

	result := &VerifyResult{
		Valid: resp.GetValid(),
	}

	if resp.HasSignerName() {
		result.SignerName = resp.GetSignerName()
	}
	if resp.HasDocumentId() {
		result.DocumentID = resp.GetDocumentId()
	}

	return result, nil
}

// Lookup retrieves document information
func (c *Client) Lookup(ctx context.Context, documentID string) (*LookupResult, error) {
	resp, _, err := c.api.LookupAPI.LookupDocumentApiV1LookupDocumentIdGet(ctx, documentID).Execute()
	if err != nil {
		return nil, err
	}

	result := &LookupResult{
		DocumentID: documentID,
	}

	if resp.HasTitle() {
		result.Title = resp.GetTitle()
	}
	if resp.HasSignerName() {
		result.SignerName = resp.GetSignerName()
	}

	return result, nil
}
