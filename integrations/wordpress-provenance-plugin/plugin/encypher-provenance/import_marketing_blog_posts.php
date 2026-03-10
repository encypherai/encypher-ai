<?php

if (!defined('ABSPATH')) {
    require_once '/var/www/html/wp-load.php';
}

require_once ABSPATH . 'wp-admin/includes/taxonomy.php';

$dataset = __DIR__ . '/data/marketing-blog-posts.json';
if (!file_exists($dataset)) {
    fwrite(STDERR, "Dataset missing: {$dataset}\n");
    exit(1);
}

$raw = file_get_contents($dataset);
$posts = json_decode($raw, true);
if (!is_array($posts)) {
    fwrite(STDERR, "Invalid dataset JSON\n");
    exit(1);
}

$existing = get_posts([
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1,
    'fields' => 'ids',
]);

foreach ($existing as $post_id) {
    wp_delete_post($post_id, true);
}

echo 'DELETED_EXISTING_POSTS ' . count($existing) . PHP_EOL;

foreach (['Encypher Insights', 'AI Policy', 'Content Provenance'] as $category_name) {
    if (!term_exists($category_name, 'category')) {
        wp_insert_term($category_name, 'category');
    }
}

$count = 0;
foreach ($posts as $post) {
    $title = isset($post['title']) ? wp_strip_all_tags((string) $post['title']) : ('Post ' . ($count + 1));
    $content = isset($post['content']) ? (string) $post['content'] : '';
    $slug = isset($post['slug']) ? sanitize_title((string) $post['slug']) : sanitize_title($title);
    $date = isset($post['date']) ? gmdate('Y-m-d 09:i:s', strtotime((string) $post['date'])) : gmdate('Y-m-d H:i:s');
    $post_id = wp_insert_post([
        'post_title' => $title,
        'post_content' => $content,
        'post_name' => $slug,
        'post_status' => 'publish',
        'post_type' => 'post',
        'post_author' => 1,
        'post_date' => $date,
        'post_date_gmt' => get_gmt_from_date($date),
        'post_excerpt' => isset($post['excerpt']) ? (string) $post['excerpt'] : '',
    ], true);

    if (is_wp_error($post_id)) {
        fwrite(STDERR, 'INSERT_ERROR ' . $title . ' ' . $post_id->get_error_message() . PHP_EOL);
        exit(1);
    }

    if (!empty($post['tags']) && is_array($post['tags'])) {
        wp_set_post_tags($post_id, array_map('strval', $post['tags']));
    }

    wp_set_post_categories($post_id, [get_cat_ID('Encypher Insights')]);
    update_post_meta($post_id, '_encypher_demo_source', 'marketing_blog');
    update_post_meta($post_id, '_encypher_demo_author', isset($post['author']) ? (string) $post['author'] : 'Encypher Editorial Team');
    $count++;
}

echo 'IMPORT_DONE ' . json_encode(['count' => $count]) . PHP_EOL;
