<?php
/**
 * Temporary script to flush WordPress rewrite rules
 * Access via: http://localhost:8080/wp-content/plugins/encypher-provenance/../../flush-rewrites.php
 * Or place in WordPress root and access: http://localhost:8080/flush-rewrites.php
 */

// Load WordPress
require_once(__DIR__ . '/../../wordpress/wp-load.php');

// Flush rewrite rules
flush_rewrite_rules();

echo "✅ Rewrite rules flushed successfully!\n";
echo "You can now access: http://localhost:8080/c2pa-verify/{instance_id}\n";
echo "\nPlease delete this file after use for security.";
