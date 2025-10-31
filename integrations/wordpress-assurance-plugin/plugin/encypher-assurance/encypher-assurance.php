<?php
/**
 * Plugin Name:       Encypher C2PA - Text Authentication
 * Plugin URI:        https://encypherai.com/wordpress
 * Description:       C2PA-compliant text authentication. Embed cryptographic proof of origin into your WordPress content. Built on standards we're developing with Google, BBC, OpenAI, Adobe, and Microsoft.
 * Version:           1.0.0
 * Requires at least: 6.0
 * Requires PHP:      7.4
 * Author:            Encypher Corporation
 * Author URI:        https://encypherai.com/
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       encypher-assurance
 * Domain Path:       /languages
 */

if (! defined('ABSPATH')) {
    exit;
}

if (! defined('ENCYPHER_ASSURANCE_VERSION')) {
    define('ENCYPHER_ASSURANCE_VERSION', '1.0.0');
}

define('ENCYPHER_ASSURANCE_PLUGIN_FILE', __FILE__);
define('ENCYPHER_ASSURANCE_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('ENCYPHER_ASSURANCE_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once ENCYPHER_ASSURANCE_PLUGIN_DIR . 'includes/class-encypher-assurance.php';

\EncypherAssurance\Plugin::get_instance();
