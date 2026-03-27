<?php
/**
 * Plugin Name:       Encypher Provenance
 * Plugin URI:        https://encypher.com/wordpress
 * Description:       C2PA-compliant text authentication. Embed cryptographic proof of origin into your WordPress content. Built on standards we're developing with Google, BBC, OpenAI, Adobe, and Microsoft.
 * Version:           1.1.0
 * Requires at least: 6.0
 * Requires PHP:      7.4
 * Author:            Encypher Corporation
 * Author URI:        https://encypher.com/
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       encypher-provenance
 * Domain Path:       /languages
 */

if (! defined('ABSPATH')) {
    exit;
}

if (! defined('ENCYPHER_PROVENANCE_VERSION')) {
    define('ENCYPHER_PROVENANCE_VERSION', '1.1.0');
}

define('ENCYPHER_PROVENANCE_PLUGIN_FILE', __FILE__);
define('ENCYPHER_PROVENANCE_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('ENCYPHER_PROVENANCE_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once ENCYPHER_PROVENANCE_PLUGIN_DIR . 'includes/class-encypher-provenance.php';

\EncypherProvenance\Plugin::get_instance();
