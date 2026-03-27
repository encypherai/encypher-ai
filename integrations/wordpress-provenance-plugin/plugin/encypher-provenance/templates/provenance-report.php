<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>C2PA Provenance Report - Encypher</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header {
            background: #1B2F50;
            color: white;
            padding: 30px;
            border-radius: 12px 12px 0 0;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            font-weight: 500;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .content {
            background: white;
            padding: 40px;
            border-radius: 0 0 12px 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .status-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: 600;
            margin-bottom: 30px;
        }
        .status-verified {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            font-size: 20px;
            color: #1B2F50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #B7D5ED;
        }
        .info-grid {
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .info-label {
            font-weight: 600;
            color: #666;
        }
        .info-value {
            color: #333;
        }
        .code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            word-break: break-all;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }
        .footer a {
            color: #2A87C4;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>C2PA Provenance Report</h1>
            <p>Content Authenticity & Provenance Verification</p>
        </div>

        <div class="content">
            <?php if (is_wp_error($data)): ?>
                <div class="status-badge" style="background: #f8d7da; color: #721c24; border-color: #f5c6cb;">
                    Not Found
                </div>
                <p><?php echo esc_html($data->get_error_message()); ?></p>
            <?php else: ?>
                <div class="status-badge status-verified">
                    Verified Content
                </div>

                <?php $report = $data->get_data(); ?>

                <?php if (!empty($report['post'])): ?>
                <div class="section">
                    <h2>Content Information</h2>
                    <div class="info-grid">
                        <div class="info-label">Title:</div>
                        <div class="info-value"><?php echo esc_html($report['post']['title']); ?></div>

                        <div class="info-label">Author:</div>
                        <div class="info-value"><?php echo esc_html($report['post']['author']); ?></div>

                        <div class="info-label">Published:</div>
                        <div class="info-value"><?php echo esc_html($report['post']['published']); ?></div>

                        <div class="info-label">Last Modified:</div>
                        <div class="info-value"><?php echo esc_html($report['post']['modified']); ?></div>

                        <div class="info-label">URL:</div>
                        <div class="info-value"><a href="<?php echo esc_url($report['post']['url']); ?>" target="_blank"><?php echo esc_html($report['post']['url']); ?></a></div>
                    </div>
                </div>
                <?php endif; ?>

                <?php if (!empty($report['c2pa'])): ?>
                <div class="section">
                    <h2>C2PA Signature</h2>
                    <div class="info-grid">
                        <div class="info-label">Document ID:</div>
                        <div class="info-value"><span class="code"><?php echo esc_html($report['c2pa']['document_id']); ?></span></div>

                        <div class="info-label">Status:</div>
                        <div class="info-value"><?php echo esc_html($report['c2pa']['status']); ?></div>

                        <div class="info-label">Last Signed:</div>
                        <div class="info-value"><?php echo esc_html($report['c2pa']['last_signed']); ?></div>

                        <?php if ($report['c2pa']['last_verified']): ?>
                        <div class="info-label">Last Verified:</div>
                        <div class="info-value"><?php echo esc_html($report['c2pa']['last_verified']); ?></div>
                        <?php endif; ?>
                    </div>
                </div>
                <?php endif; ?>

                <?php if (!empty($report['verification'])): ?>
                <div class="section">
                    <h2>Verification Details</h2>
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 12px;"><?php echo esc_html(json_encode($report['verification'], JSON_PRETTY_PRINT)); ?></pre>
                </div>
                <?php endif; ?>
            <?php endif; ?>
        </div>

        <div class="footer">
            <p>Powered by <a href="https://encypher.com" target="_blank">Encypher</a></p>
            <p style="margin-top: 10px; font-size: 12px;">This report verifies the authenticity and provenance of the content using C2PA standards.</p>
        </div>
    </div>
</body>
</html>
