<?php
namespace EncypherProvenance;

if (! defined('ABSPATH')) {
    exit;
}

require_once ENCYPHER_PROVENANCE_PLUGIN_DIR . 'includes/class-encypher-provenance-html-parser.php';
require_once ENCYPHER_PROVENANCE_PLUGIN_DIR . 'includes/class-encypher-provenance-admin.php';
require_once ENCYPHER_PROVENANCE_PLUGIN_DIR . 'includes/class-encypher-provenance-rest.php';
require_once ENCYPHER_PROVENANCE_PLUGIN_DIR . 'includes/class-encypher-provenance-verification.php';
require_once ENCYPHER_PROVENANCE_PLUGIN_DIR . 'includes/class-encypher-provenance-bulk.php';
require_once ENCYPHER_PROVENANCE_PLUGIN_DIR . 'includes/class-encypher-provenance-frontend.php';
require_once ENCYPHER_PROVENANCE_PLUGIN_DIR . 'includes/class-encypher-provenance-coalition.php';

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
    private Frontend $frontend;
    private Coalition $coalition;

    private function __construct()
    {
        $this->admin = new Admin();
        $this->rest = new Rest();
        $this->verification = new Verification($this->rest);
        $this->bulk = new Bulk();
        $this->frontend = new Frontend();
        $this->coalition = new Coalition();

        register_activation_hook(ENCYPHER_PROVENANCE_PLUGIN_FILE, [self::class, 'activate']);
        register_deactivation_hook(ENCYPHER_PROVENANCE_PLUGIN_FILE, [self::class, 'deactivate']);

        add_action('init', [$this, 'load_textdomain']);
        add_action('init', [$this, 'add_rewrite_rules']);
        add_action('init', [$this, 'handle_c2pa_verify_page'], 999); // Very late priority
        add_filter('query_vars', [$this, 'add_query_vars']);
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
            'tier' => 'free',
        ];

        $options = get_option('encypher_provenance_settings', []);
        update_option('encypher_provenance_settings', wp_parse_args($options, $defaults));
        
        // Add rewrite rules before flushing
        add_rewrite_rule(
            '^c2pa-verify/([^/]+)/?$',
            'index.php?c2pa_verify=1&instance_id=$matches[1]',
            'top'
        );
        
        // Flush rewrite rules on activation
        flush_rewrite_rules();
    }

    public static function deactivate(): void
    {
        // Intentionally left empty. We keep settings and meta data for future re-activation.
    }

    /**
     * Return the URL slug used for the C2PA verification page.
     */
    public static function get_verify_slug(): string
    {
        return 'c2pa-verify';
    }

    public function load_textdomain(): void
    {
        load_plugin_textdomain('encypher-provenance', false, dirname(plugin_basename(ENCYPHER_PROVENANCE_PLUGIN_FILE)) . '/languages/');
    }

    public function boot(): void
    {
        $this->admin->register_hooks();
        $this->rest->register_hooks();
        $this->verification->register_hooks();
        $this->bulk->register_hooks();
        $this->frontend->register_hooks();
        $this->coalition->register_hooks();
    }
    
    public function add_rewrite_rules(): void
    {
        // Add rewrite rule for /c2pa-verify/{instance_id}
        add_rewrite_rule(
            '^c2pa-verify/([^/]+)/?$',
            'index.php?c2pa_verify=1&instance_id=$matches[1]',
            'top'
        );
    }
    
    public function add_query_vars($vars): array
    {
        $vars[] = 'c2pa_verify';
        $vars[] = 'instance_id';
        return $vars;
    }
    
    public function handle_c2pa_verify_page(): void
    {
        // Check if this is a c2pa-verify URL by parsing the request URI
        $request_uri = $_SERVER['REQUEST_URI'] ?? '';
        
        if (preg_match('#^/c2pa-verify/([^/]+)/?$#', $request_uri, $matches)) {
            $instance_id = $matches[1];
            
            // Create REST request
            $request = new \WP_REST_Request('GET', '/encypher-provenance/v1/provenance');
            $request->set_param('instance_id', $instance_id);
            
            // Get the data
            $data = $this->rest->handle_provenance_request($request);
            
            // Load template
            include ENCYPHER_PROVENANCE_PLUGIN_DIR . 'templates/provenance-report.php';
            exit;
        }
        
        // Also try query vars method
        $c2pa_verify = get_query_var('c2pa_verify');
        $instance_id_qv = get_query_var('instance_id');
        
        if ($c2pa_verify && $instance_id_qv) {
            // Create REST request
            $request = new \WP_REST_Request('GET', '/encypher-provenance/v1/provenance');
            $request->set_param('instance_id', $instance_id_qv);
            
            // Get the data
            $data = $this->rest->handle_provenance_request($request);
            
            // Load template
            include ENCYPHER_PROVENANCE_PLUGIN_DIR . 'templates/provenance-report.php';
            exit;
        }
    }
}
