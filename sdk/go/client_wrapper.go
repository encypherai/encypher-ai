// Package encypher provides a client for the Encypher Enterprise API.
//
// This is an auto-generated SDK. For the source, see:
// https://github.com/encypherai/encypherai-commercial/tree/main/sdk
//
// Usage:
//
//	client := encypher.NewClient("your_api_key")
//	result, err := client.Sign(ctx, "Hello, world!")
//	if err != nil {
//	    log.Fatal(err)
//	}
//	fmt.Println(result.SignedText)
package encypher

import (
	"context"
)

// Client is a high-level client for the Encypher Enterprise API.
type Client struct {
	apiKey  string
	baseURL string
	api     *APIClient
}

// NewClient creates a new Encypher client.
func NewClient(apiKey string) *Client {
	return NewClientWithURL(apiKey, "https://api.encypherai.com")
}

// NewClientWithURL creates a new Encypher client with a custom base URL.
func NewClientWithURL(apiKey, baseURL string) *Client {
	cfg := NewConfiguration()
	cfg.Servers = ServerConfigurations{{URL: baseURL}}
	cfg.AddDefaultHeader("Authorization", "Bearer "+apiKey)
	
	return &Client{
		apiKey:  apiKey,
		baseURL: baseURL,
		api:     NewAPIClient(cfg),
	}
}

// Sign signs content with a C2PA manifest.
func (c *Client) Sign(ctx context.Context, text string) (*SignResponse, error) {
	req := NewSignRequest(text)
	return c.api.SigningAPI.SignContentApiV1SignPost(ctx).SignRequest(*req).Execute()
}

// Verify verifies signed content.
func (c *Client) Verify(ctx context.Context, text string) (*VerifyResponse, error) {
	req := NewVerifyRequest(text)
	return c.api.VerificationAPI.VerifyContentApiV1VerifyPost(ctx).VerifyRequest(*req).Execute()
}
