# Architecture Boundaries and Ecosystem Positioning

## Purpose

This document clarifies what is standards-based, what the current plugin does, what Encypher hosts today, and what could reasonably evolve into broader WordPress ecosystem capabilities.

## The architectural position

The Encypher WordPress plugin should be understood as a working implementation of a broader provenance workflow.

It is not the claim that WordPress core should depend on one vendor backend.

It is the claim that WordPress should be able to support provenance and authenticity workflows cleanly.

## What is standards-based

These parts are intended to be interoperable and ecosystem-friendly:

- C2PA-aligned proof of origin
- provenance metadata attached to text content
- provenance preserved across edits
- public verification as a user-facing trust surface
- programmatic verification and workflow integration around signed content

## What the plugin does today

Inside WordPress, the plugin currently provides:

- a WordPress-native install and settings experience
- secure email-based workspace connection
- optional manual API key fallback
- automatic signing on publish and update
- verification status in WordPress surfaces
- public verification badge on the frontend
- analytics and coverage views for WordPress teams
- bulk-signing support for older content

## What Encypher hosts today

The hosted service currently provides:

- workspace identity and provisioning
- signing services
- verification services
- account and billing management
- advanced enterprise capabilities

This is an implementation choice for the current product.

It should not be presented as the only possible architecture for provenance in WordPress.

## What could become a broader WordPress capability

The most plausible ecosystem or platform abstractions are:

- a provenance/authenticity interface for content workflows
- editor-side provenance metadata surfaces
- hooks for publish, update, and verification events
- frontend verification rendering hooks
- plugin interoperability around signed content and verification state
- patterns for AI-assisted content to preserve provenance through WordPress workflows

## The provider-neutral framing

A clean way to describe the current state is:

- WordPress can expose provenance-friendly surfaces and extensibility points
- plugins and services can implement different signing and verification providers
- Encypher is demonstrating one production-ready path using open standards

## Why this matters for AI-era WordPress

As WordPress adds more AI-assisted authoring, agentic publishing, and content workflow automation, provenance becomes more important, not less.

Key future use cases include:

- distinguishing authored content from transformed content
- preserving provenance through editorial revisions
- making authenticity visible to readers
- giving plugins and agents a standard place to participate in trust workflows

## The right discussion question for Anne and James

Not:

"Should WordPress adopt our service?"

But:

"What would the right provenance abstraction look like in a WordPress ecosystem that wants to remain open, extensible, and ready for AI-assisted publishing?"
