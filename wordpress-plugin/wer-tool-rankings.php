<?php
/**
 * Plugin Name: WER Tool Rankings
 * Description: Display top 10 AI tools ranked by lowest WER (Word Error Rate)
 * Version: 1.0.0
 * Author: WER Automation
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Add the shortcode
add_shortcode('wer_tool_rankings', 'wer_render_tool_rankings');

/**
 * Main function to render the WER tool rankings
 */
function wer_render_tool_rankings($atts) {
    // Parse shortcode attributes
    $atts = shortcode_atts(array(
        'backend_url' => 'https://wer-automation-api.onrender.com'
    ), $atts);

    ob_start();
    ?>
    <div class="wer-rankings-container">
        <style>
            .wer-rankings-container {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1000px;
                margin: 20px auto;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .wer-title {
                text-align: center;
                margin-bottom: 30px;
            }

            .wer-title h2 {
                color: #333;
                margin: 0 0 10px 0;
            }

            .wer-controls {
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
                flex-wrap: wrap;
                justify-content: center;
                align-items: flex-end;
            }

            .wer-control-group {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }

            .wer-control-group label {
                font-weight: 600;
                color: #555;
                font-size: 14px;
            }

            .wer-control-group select {
                padding: 10px 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                min-width: 200px;
                background: white;
            }

            .wer-control-group button {
                padding: 10px 25px;
                background: #0073aa;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: background 0.3s;
            }

            .wer-control-group button:hover {
                background: #005a87;
            }

            .wer-loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }

            .wer-loading-spinner {
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #0073aa;
                border-radius: 50%;
                animation: wer-spin 1s linear infinite;
            }

            @keyframes wer-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .wer-error {
                background: #fee;
                color: #c00;
                padding: 15px;
                border-radius: 4px;
                border-left: 4px solid #c00;
            }

            .wer-warning {
                background: #ffeaa7;
                color: #856404;
                padding: 15px;
                border-radius: 4px;
                border-left: 4px solid #ffc107;
            }

            .wer-table-wrapper {
                overflow-x: auto;
            }

            .wer-rankings-table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                border-radius: 4px;
                overflow: hidden;
            }

            .wer-rankings-table thead {
                background: linear-gradient(135deg, #0073aa 0%, #005a87 100%);
                color: white;
            }

            .wer-rankings-table th {
                padding: 15px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #005a87;
            }

            .wer-rankings-table td {
                padding: 12px 15px;
                border-bottom: 1px solid #eee;
            }

            .wer-rankings-table tbody tr {
                transition: background 0.2s;
            }

            .wer-rankings-table tbody tr:hover {
                background: #f5f5f5;
            }

            .wer-rank {
                font-weight: 700;
                font-size: 18px;
                text-align: center;
                min-width: 60px;
            }

            .wer-rank.rank-1 {
                color: #d4af37;
                font-size: 20px;
            }

            .wer-rank.rank-2 {
                color: #c0c0c0;
                font-size: 20px;
            }

            .wer-rank.rank-3 {
                color: #cd7f32;
                font-size: 20px;
            }

            .wer-metrics {
                text-align: center;
                font-weight: 600;
                color: #0073aa;
            }

            .wer-metric-badge {
                display: inline-block;
                background: #e8f4f9;
                color: #0073aa;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 700;
                min-width: 80px;
                text-align: center;
            }

            .wer-footer {
                margin-top: 20px;
                text-align: center;
                color: #999;
                font-size: 12px;
            }

            @media (max-width: 768px) {
                .wer-controls {
                    flex-direction: column;
                    align-items: stretch;
                }

                .wer-control-group select {
                    min-width: 100%;
                }

                .wer-rankings-table {
                    font-size: 13px;
                }

                .wer-rankings-table th,
                .wer-rankings-table td {
                    padding: 8px 10px;
                }
            }
        </style>

        <div class="wer-title">
            <h2>🏆 AI Tools Rankings - Word Error Rate</h2>
            <p>Top 10 tools ranked by lowest average WER (Lower is Better)</p>
        </div>

        <div class="wer-controls">
            <div class="wer-control-group">
                <label for="wer-language-select">Select Language:</label>
                <select id="wer-language-select">
                    <option value="hi">Hindi</option>
                    <option value="pa">Punjabi</option>
                    <option value="te">Telugu</option>
                    <option value="mr">Marathi</option>
                </select>
            </div>

            <div class="wer-control-group">
                <button type="button" onclick="wer_load_rankings()">
                    Load Rankings
                </button>
            </div>
        </div>

        <div id="wer-content">
            <div class="wer-loading">
                <div class="wer-loading-spinner"></div>
                <p>Loading rankings...</p>
            </div>
        </div>

        <div class="wer-footer">
            <p>Top 10 AI Tools Rankings - Aggregated Across All Months</p>
        </div>
    </div>

    <script>
        const WER_CONFIG = {
            backendUrl: '<?php echo $atts['backend_url']; ?>'
        };

        // Load rankings on page load
        window.addEventListener('load', function() {
            wer_load_rankings();
        });

        function wer_load_rankings() {
            const language = document.getElementById('wer-language-select').value;
            const contentDiv = document.getElementById('wer-content');

            // Show loading state
            contentDiv.innerHTML = '<div class="wer-loading"><div class="wer-loading-spinner"></div><p>Loading rankings...</p></div>';

            // Build API URL - only language parameter needed
            const apiUrl = `${WER_CONFIG.backendUrl}/api/wer/get-tool-summary-metrics?language=${language}`;

            // Fetch data from backend
            fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.data && Object.keys(data.data).length > 0) {
                    wer_render_table(data.data);
                } else if (data.status === 'warning') {
                    contentDiv.innerHTML = `<div class="wer-warning">⚠️ ${data.message}</div>`;
                } else {
                    contentDiv.innerHTML = `<div class="wer-error">❌ Error: ${data.message || 'Unable to load rankings'}</div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                contentDiv.innerHTML = `<div class="wer-error">❌ Error loading rankings: ${error.message}</div>`;
            });
        }

        function wer_render_table(toolsData) {
            const contentDiv = document.getElementById('wer-content');

            // Convert to array and sort by average_wer (ascending)
            const toolsArray = Object.entries(toolsData).map(([tool, metrics]) => ({
                tool: tool,
                avgWer: parseFloat(metrics.average_wer) || 0,
                bestWer: parseFloat(metrics.best_wer) || 0,
                worstWer: parseFloat(metrics.worst_wer) || 0,
                fileCount: metrics.files_count || 0
            }));

            // Sort by average WER (lowest first = best)
            toolsArray.sort((a, b) => a.avgWer - b.avgWer);

            // Get top 10
            const top10 = toolsArray.slice(0, 10);

            if (top10.length === 0) {
                contentDiv.innerHTML = '<div class="wer-warning">⚠️ No data available for this language</div>';
                return;
            }

            // Build table HTML
            let tableHtml = `
                <div class="wer-table-wrapper">
                    <table class="wer-rankings-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>AI Tool</th>
                                <th>Average WER</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            top10.forEach((item, index) => {
                const rank = index + 1;
                const rankClass = rank <= 3 ? `rank-${rank}` : '';
                const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `#${rank}`;

                tableHtml += `
                    <tr>
                        <td class="wer-rank ${rankClass}">${medal}</td>
                        <td><strong>${wer_escape_html(item.tool)}</strong></td>
                        <td class="wer-metrics"><span class="wer-metric-badge">${item.avgWer.toFixed(2)}%</span></td>
                    </tr>
                `;
            });

            tableHtml += `
                        </tbody>
                    </table>
                </div>
            `;

            contentDiv.innerHTML = tableHtml;
        }

        function wer_escape_html(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
    </script>

    <?php
    return ob_get_clean();
}

// Add admin menu to test the plugin
add_action('admin_menu', 'wer_add_admin_menu');

function wer_add_admin_menu() {
    add_menu_page(
        'WER Rankings',
        'WER Rankings',
        'manage_options',
        'wer-rankings',
        'wer_admin_page'
    );
}

function wer_admin_page() {
    ?>
    <div class="wrap">
        <h1>WER Tool Rankings</h1>
        <p>Use the shortcode <code>[wer_tool_rankings]</code> on any page or post to display the rankings.</p>
        <p>You can customize it with attributes:</p>
        <ul>
            <li><code>[wer_tool_rankings year="2024" month="January"]</code></li>
            <li><code>[wer_tool_rankings backend_url="https://your-api.com"]</code></li>
        </ul>
    </div>
    <?php
}
?>
