<?php
/**
 * Content Provenance Experiment (draft for upstream contribution to WordPress/ai)
 *
 * This file is a DRAFT intended for contribution to the WordPress/ai plugin.
 * It would live at: includes/Experiments/Content_Provenance/class-content-provenance.php
 *
 * @package WordPress_AI\Experiments\Content_Provenance
 * @since   TBD
 */

namespace WP_AI\Experiments\Content_Provenance;

use WP_AI\Abstracts\Abstract_Experiment;

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Content Provenance Experiment.
 *
 * Auto-signs AI-generated content with C2PA-compatible provenance via the
 * Encypher API. Hooks into all AI experiment output filters and embeds
 * an invisible Unicode watermark before the content is committed.
 *
 * @since TBD
 */
class Content_Provenance extends Abstract_Experiment {

	const EXPERIMENT_SLUG = 'content-provenance';

	/**
	 * The Encypher API base URL.
	 */
	const API_BASE = 'https://api.encypher.com/api/v1';

	/**
	 * Get the experiment slug.
	 *
	 * @return string
	 */
	public function get_slug(): string {
		return self::EXPERIMENT_SLUG;
	}

	/**
	 * Get the experiment label.
	 *
	 * @return string
	 */
	public function get_label(): string {
		return __( 'Content Provenance (Encypher)', 'wordpress-ai' );
	}

	/**
	 * Get the experiment description.
	 *
	 * @return string
	 */
	public function get_description(): string {
		return __( 'Automatically embeds C2PA-compatible cryptographic provenance into AI-generated content. Signed content can be publicly verified to confirm which AI model generated it, when, and from what source.', 'wordpress-ai' );
	}

	/**
	 * Get settings fields for this experiment.
	 *
	 * @return array
	 */
	public function get_fields(): array {
		return [
			[
				'key'         => 'encypher_api_key',
				'label'       => __( 'Encypher API Key', 'wordpress-ai' ),
				'type'        => 'password',
				'description' => __( 'Required. Get your free API key at encypher.com. Free tier: 1,000 signs/month.', 'wordpress-ai' ),
				'required'    => true,
			],
			[
				'key'         => 'embed_watermark',
				'label'       => __( 'Embed Unicode Watermark', 'wordpress-ai' ),
				'type'        => 'checkbox',
				'default'     => true,
				'description' => __( 'Embeds an invisible watermark that survives copy-paste out of WordPress.', 'wordpress-ai' ),
			],
		];
	}

	/**
	 * Register WordPress hooks for this experiment.
	 * Called only when the experiment is enabled.
	 */
	public function register_hooks(): void {
		add_filter( 'wp_ai_experiment_title_generation_result',   [ $this, 'sign_content' ], 10, 2 );
		add_filter( 'wp_ai_experiment_excerpt_generation_result', [ $this, 'sign_content' ], 10, 2 );
		add_filter( 'wp_ai_experiment_summary_generation_result', [ $this, 'sign_content' ], 10, 2 );
		add_filter( 'wp_ai_experiment_review_notes_result',       [ $this, 'sign_content' ], 10, 2 );
		add_filter( 'wp_ai_experiment_alt_text_result',           [ $this, 'sign_content' ], 10, 2 );
	}

	/**
	 * Sign AI-generated content with Encypher provenance.
	 *
	 * @param string $content The AI-generated content.
	 * @param array  $context Experiment context (model, provider, post_id, etc.)
	 * @return string Signed content or original content on failure.
	 */
	public function sign_content( string $content, array $context = [] ): string {
		if ( empty( trim( $content ) ) ) {
			return $content;
		}

		$api_key = $this->get_option( 'encypher_api_key', '' );
		if ( empty( $api_key ) ) {
			return $content;
		}

		$metadata = array_filter( [
			'source'      => 'wordpress-ai',
			'generator'   => $context['model'] ?? $context['provider'] ?? null,
			'experiment'  => current_filter(),
			'post_id'     => $context['post_id'] ?? null,
			'generated_at'=> gmdate( 'c' ),
		] );

		$response = wp_remote_post(
			self::API_BASE . '/sign',
			[
				'headers' => [
					'Authorization' => 'Bearer ' . $api_key,
					'Content-Type'  => 'application/json',
				],
				'body'    => wp_json_encode( [ 'text' => $content, 'metadata' => $metadata ] ),
				'timeout' => 20,
			]
		);

		if ( is_wp_error( $response ) ) {
			return $content;
		}

		$status = wp_remote_retrieve_response_code( $response );
		if ( $status < 200 || $status >= 300 ) {
			return $content;
		}

		$data        = json_decode( wp_remote_retrieve_body( $response ), true );
		$signed_text = $data['signed_text'] ?? $data['data']['signed_text'] ?? null;

		return is_string( $signed_text ) && ! empty( $signed_text ) ? $signed_text : $content;
	}
}
