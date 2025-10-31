<?php
namespace EncypherAssurance;

if (! defined('ABSPATH')) {
    exit;
}

require_once ENCYPHER_ASSURANCE_PLUGIN_DIR . 'includes/class-encypher-assurance-admin.php';
require_once ENCYPHER_ASSURANCE_PLUGIN_DIR . 'includes/class-encypher-assurance-rest.php';
require_once ENCYPHER_ASSURANCE_PLUGIN_DIR . 'includes/class-encypher-assurance-verification.php';
require_once ENCYPHER_ASSURANCE_PLUGIN_DIR . 'includes/class-encypher-assurance-bulk.php';

/**
 * Main plugin bootstrap class.
 */
class Plugin
{
    private static ?Plugin $instance = null;

    private Admin $admin;
    private Rest $rest;
    private Verification $verification;
    private Bulk $bulk;

    private function __construct()
    {
        $this->admin = new Admin();
        $this->rest = new Rest();
        $this->verification = new Verification($this->rest);
        $this->bulk = new Bulk();

        register_activation_hook(ENCYPHER_ASSURANCE_PLUGIN_FILE, [self::class, 'activate']);
        register_deactivation_hook(ENCYPHER_ASSURANCE_PLUGIN_FILE, [self::class, 'deactivate']);

        add_action('init', [$this, 'load_textdomain']);
        add_action('plugins_loaded', [$this, 'boot']);
    }

    public static function get_instance(): Plugin
    {
        if (null === self::$instance) {
            self::$instance = new self();
        }

        return self::$instance;
    }

    public static function activate(): void
    {
        $defaults = [
            'api_base_url' => 'https://api.encypherai.com/api/v1',
            'api_key' => '',
            'auto_verify' => true,
        ];

        $options = get_option('encypher_assurance_settings', []);
        update_option('encypher_assurance_settings', wp_parse_args($options, $defaults));
    }

    public static function deactivate(): void
    {
        // Intentionally left empty. We keep settings and meta data for future re-activation.
    }

    public function load_textdomain(): void
    {
        load_plugin_textdomain('encypher-assurance', false, dirname(plugin_basename(ENCYPHER_ASSURANCE_PLUGIN_FILE)) . '/languages/');
    }

    public function boot(): void
    {
        $this->admin->register_hooks();
        $this->rest->register_hooks();
        $this->verification->register_hooks();
        $this->bulk->register_hooks();
    }
}
