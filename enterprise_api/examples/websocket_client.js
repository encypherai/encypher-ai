/**
 * Example WebSocket client for testing streaming API (Node.js)
 * 
 * Usage:
 *   npm install ws
 *   node examples/websocket_client.js
 */

const WebSocket = require('ws');

// Configuration
const API_KEY = 'demo_key_12345'; // Replace with your API key
const WS_URL = `ws://localhost:8000/api/v1/sign/stream?api_key=${API_KEY}`;

async function testStreaming() {
    console.log('Connecting to', WS_URL);
    
    const ws = new WebSocket(WS_URL);
    
    return new Promise((resolve, reject) => {
        ws.on('open', () => {
            console.log('✅ Connected!');
        });
        
        ws.on('message', (data) => {
            const message = JSON.parse(data.toString());
            
            switch (message.type) {
                case 'connected':
                    console.log('✅ Session ID:', message.session_id);
                    
                    // Send test chunks
                    const chunks = [
                        'This is the first sentence. ',
                        'Here comes the second sentence. ',
                        'And finally, the third sentence.'
                    ];
                    
                    console.log(`\n📤 Sending ${chunks.length} chunks...`);
                    
                    chunks.forEach((chunk, i) => {
                        console.log(`\n  Chunk ${i + 1}: ${chunk.substring(0, 50)}...`);
                        ws.send(JSON.stringify({
                            type: 'chunk',
                            content: chunk,
                            chunk_id: `chunk_${String(i).padStart(3, '0')}`
                        }));
                    });
                    
                    // Finalize after a short delay
                    setTimeout(() => {
                        console.log('\n📤 Finalizing stream...');
                        ws.send(JSON.stringify({ type: 'finalize' }));
                    }, 1000);
                    break;
                
                case 'signed_chunk':
                    const signed = message.signed ? '✅ SIGNED' : '⚠️  NOT SIGNED';
                    console.log(`  ${signed}`);
                    console.log(`  Content preview: ${message.content.substring(0, 80)}...`);
                    break;
                
                case 'complete':
                    console.log('\n✅ Stream complete!');
                    console.log('  Document ID:', message.document_id);
                    console.log('  Total chunks:', message.total_chunks);
                    console.log('  Duration:', message.duration_seconds?.toFixed(2) + 's');
                    console.log('  Verification URL:', message.verification_url);
                    
                    ws.close();
                    resolve(0);
                    break;
                
                case 'error':
                    console.error('❌ Error:', message.message);
                    ws.close();
                    reject(new Error(message.message));
                    break;
                
                default:
                    console.log('📨 Server:', message);
            }
        });
        
        ws.on('error', (error) => {
            console.error('❌ WebSocket error:', error.message);
            reject(error);
        });
        
        ws.on('close', () => {
            console.log('\n🔌 Connection closed');
        });
    });
}

async function testRateLimiting() {
    console.log('\n🔥 Testing rate limiting...');
    console.log('Connecting to', WS_URL);
    
    const ws = new WebSocket(WS_URL);
    
    return new Promise((resolve, reject) => {
        let rateLimited = false;
        let chunksSent = 0;
        
        ws.on('open', () => {
            console.log('✅ Connected!');
        });
        
        ws.on('message', (data) => {
            const message = JSON.parse(data.toString());
            
            if (message.type === 'connected') {
                console.log('📤 Sending 100 chunks rapidly...');
                
                // Send chunks as fast as possible
                for (let i = 0; i < 100; i++) {
                    ws.send(JSON.stringify({
                        type: 'chunk',
                        content: `Chunk ${i}. `,
                        chunk_id: `chunk_${String(i).padStart(3, '0')}`
                    }));
                    chunksSent++;
                }
            } else if (message.type === 'error' && message.message.toLowerCase().includes('rate limit')) {
                console.log(`  ⚠️  Rate limited at chunk ${chunksSent}`);
                rateLimited = true;
                
                // Finalize and close
                ws.send(JSON.stringify({ type: 'finalize' }));
            } else if (message.type === 'complete') {
                if (rateLimited) {
                    console.log('✅ Rate limiting is working!');
                } else {
                    console.log('⚠️  No rate limiting detected (sent 100 chunks)');
                }
                
                ws.close();
                resolve(0);
            }
        });
        
        ws.on('error', (error) => {
            console.error('❌ Error:', error.message);
            reject(error);
        });
    });
}

async function main() {
    console.log('='.repeat(60));
    console.log('WebSocket Streaming API - Test Suite (Node.js)');
    console.log('='.repeat(60));
    
    try {
        // Test 1: Basic streaming
        await testStreaming();
        
        // Wait between tests
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Test 2: Rate limiting
        await testRateLimiting();
        
        console.log('\n' + '='.repeat(60));
        console.log('✅ All tests passed!');
        console.log('='.repeat(60));
        
        process.exit(0);
    } catch (error) {
        console.error('\n❌ Test failed:', error.message);
        process.exit(1);
    }
}

// Run tests
if (require.main === module) {
    main().catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
}

module.exports = { testStreaming, testRateLimiting };
