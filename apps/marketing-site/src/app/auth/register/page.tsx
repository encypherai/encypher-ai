"use client";

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import SignInPage from '../signin/page';

function RegisterPageContent() {
  const searchParams = useSearchParams();
  const modeParam = searchParams.get('mode');
  const initialMode = modeParam === 'signin' ? 'signin' : 'signup';

  return <SignInPage initialMode={initialMode} />;
}

export default function RegisterPage() {
  // Render the sign-in page, defaulting to sign-up mode unless mode=signin is specified
  return (
    <Suspense fallback={<div>Loading...</div>}> {/* Basic fallback, can be styled later */}
      <RegisterPageContent />
    </Suspense>
  );
}
