import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { token: string } }
) {
  try {
    // Get token from params
    const { token } = params;
    
    // Use 127.0.0.1 instead of localhost to avoid IPv6 resolution issues
    const backendBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    const verificationEndpoint = `${backendBaseUrl}/api/v1/investor-access/verify-email-access/${token}`;
    
    console.log(`Calling backend verification endpoint: ${verificationEndpoint}`);
    
    // Call the backend API to verify the token
    const response = await fetch(verificationEndpoint, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      // Add a timeout to prevent hanging requests
      signal: AbortSignal.timeout(10000) // 10 second timeout
    });

    if (!response.ok) {
      console.error(`Backend verification failed with status: ${response.status}`);
      return NextResponse.json(
        { success: false, message: 'Verification failed', error: `Status: ${response.status}` },
        { status: response.status }
      );
    }

    // Parse the response from the backend
    const data = await response.json();
    console.log('Backend verification response:', data);
    
    // Return the verification result with appropriate status
    return NextResponse.json(
      { 
        success: true, 
        message: data.message || 'Verification successful',
        access_token: data.access_token,
        expires_at: data.expires_at,
        investor_id: data.investor_id
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error during verification:', error);
    return NextResponse.json(
      { success: false, message: 'Error during verification process', error: String(error) },
      { status: 500 }
    );
  }
}
