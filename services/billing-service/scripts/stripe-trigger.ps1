# Stripe CLI Event Trigger Script
#
# Use this to test webhook handling by triggering sample events.
#
# Prerequisites:
#   1. Stripe CLI installed and logged in
#   2. stripe-listen.ps1 running in another terminal
#
# Usage:
#   .\scripts\stripe-trigger.ps1 [event_type]
#
# Examples:
#   .\scripts\stripe-trigger.ps1                    # Show menu
#   .\scripts\stripe-trigger.ps1 checkout          # Trigger checkout.session.completed
#   .\scripts\stripe-trigger.ps1 subscription      # Trigger customer.subscription.created

param(
    [string]$EventType = ""
)

$events = @{
    "checkout"     = "checkout.session.completed"
    "sub_created"  = "customer.subscription.created"
    "sub_updated"  = "customer.subscription.updated"
    "sub_deleted"  = "customer.subscription.deleted"
    "invoice_paid" = "invoice.paid"
    "invoice_fail" = "invoice.payment_failed"
    "customer"     = "customer.created"
    "payment"      = "payment_intent.succeeded"
}

function Show-Menu {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Stripe Event Trigger" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available events:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  checkout      - checkout.session.completed" -ForegroundColor White
    Write-Host "  sub_created   - customer.subscription.created" -ForegroundColor White
    Write-Host "  sub_updated   - customer.subscription.updated" -ForegroundColor White
    Write-Host "  sub_deleted   - customer.subscription.deleted" -ForegroundColor White
    Write-Host "  invoice_paid  - invoice.paid" -ForegroundColor White
    Write-Host "  invoice_fail  - invoice.payment_failed" -ForegroundColor White
    Write-Host "  customer      - customer.created" -ForegroundColor White
    Write-Host "  payment       - payment_intent.succeeded" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage: .\stripe-trigger.ps1 <event_name>" -ForegroundColor Gray
    Write-Host ""
}

function Trigger-Event {
    param([string]$event)
    
    Write-Host ""
    Write-Host "Triggering: $event" -ForegroundColor Yellow
    Write-Host ""
    
    stripe trigger $event
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Event triggered successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Failed to trigger event" -ForegroundColor Red
    }
}

# Main
if ($EventType -eq "") {
    Show-Menu
} elseif ($events.ContainsKey($EventType)) {
    Trigger-Event -event $events[$EventType]
} else {
    Write-Host "Unknown event type: $EventType" -ForegroundColor Red
    Show-Menu
}
