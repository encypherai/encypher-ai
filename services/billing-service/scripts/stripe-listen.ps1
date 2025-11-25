# Stripe CLI Local Webhook Listener
# 
# This script forwards Stripe webhook events to your local billing service.
# Works with both Docker Compose and standalone service.
# 
# Prerequisites:
#   1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
#      - Windows: scoop install stripe (or download from GitHub releases)
#      - Or: winget install Stripe.StripeCLI
#   2. Login to Stripe: stripe login
#
# Usage:
#   .\scripts\stripe-listen.ps1           # Default: localhost:8007
#   .\scripts\stripe-listen.ps1 -Port 8007  # Custom port
#
# The script will output a webhook signing secret (whsec_...) that you need
# to add to your .env file as STRIPE_WEBHOOK_SECRET

param(
    [int]$Port = 8007
)

$WEBHOOK_PATH = "/api/v1/webhooks/stripe"
$FORWARD_URL = "http://localhost:$Port$WEBHOOK_PATH"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stripe CLI Webhook Listener" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Forwarding Stripe events to: $FORWARD_URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANT: Copy the webhook signing secret (whsec_...) that appears below" -ForegroundColor Green
Write-Host "and add it to your .env file as STRIPE_WEBHOOK_SECRET" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop listening" -ForegroundColor Gray
Write-Host ""

# Forward events to local billing service
stripe listen --forward-to $FORWARD_URL `
    --events checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,invoice.paid,invoice.payment_failed,customer.created
