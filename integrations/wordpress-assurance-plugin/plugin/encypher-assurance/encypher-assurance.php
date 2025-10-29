<?php
/**
 * Plugin Name:       Encypher Assurance
 * Plugin URI:        https://encypher.ai/
 * Description:       Sign and verify WordPress content using Encypher's authenticity services.
 * Version:           0.1.0
 * Author:            Encypher
 * Author URI:        https://encypher.ai/
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       encypher-assurance
 */

if (! defined('ABSPATH')) {
    exit;
}

if (! defined('ENCYPHER_ASSURANCE_VERSION')) {
    define('ENCYPHER_ASSURANCE_VERSION', '0.1.0');
}

define('ENCYPHER_ASSURANCE_PLUGIN_FILE', __FILE__);
define('ENCYPHER_ASSURANCE_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('ENCYPHER_ASSURANCE_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once ENCYPHER_ASSURANCE_PLUGIN_DIR . 'includes/class-encypher-assurance.php';

\EncypherAssurance\Plugin::get_instance();
