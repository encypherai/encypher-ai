'use client';

import { useEffect, useRef } from 'react';
import * as CookieConsent from 'vanilla-cookieconsent';
// CSS imported in globals.css

/**
 * Cookie Consent Banner Component
 * 
 * Implements GDPR, CCPA, and other privacy regulation compliant cookie consent.
 * Uses vanilla-cookieconsent (MIT license) - https://github.com/orestbida/cookieconsent
 */
export default function CookieConsentBanner() {
  const initialized = useRef(false);
  const disableCookieConsent = process.env.NEXT_PUBLIC_DISABLE_COOKIE_CONSENT === 'true';

  useEffect(() => {
    if (disableCookieConsent) {
      return;
    }
    // Prevent double initialization in React Strict Mode
    if (initialized.current) return;
    initialized.current = true;
    
    console.log('[CookieConsent] Initializing...');
    
    CookieConsent.run({
      cookie: {
        name: 'encypher_cc',
        expiresAfterDays: 365,
      },
      categories: {
        necessary: {
          enabled: true,
          readOnly: true,
        },
        analytics: {
          enabled: false,
        },
        marketing: {
          enabled: false,
        },
      },
      guiOptions: {
        consentModal: {
          layout: 'box',
          position: 'bottom right',
          equalWeightButtons: true,
          flipButtons: false,
        },
        preferencesModal: {
          layout: 'box',
          position: 'right',
          equalWeightButtons: true,
          flipButtons: false,
        },
      },
      language: {
        default: 'en',
        translations: {
          en: {
            consentModal: {
              title: 'We value your privacy',
              description: 'We use cookies to enhance your browsing experience and analyze site traffic. By clicking "Accept All", you consent to our use of cookies.',
              acceptAllBtn: 'Accept All',
              acceptNecessaryBtn: 'Reject All',
              showPreferencesBtn: 'Manage Preferences',
              footer: '<a href="https://encypherai.com/privacy">Privacy Policy</a> | <a href="https://encypherai.com/terms">Terms</a>',
            },
            preferencesModal: {
              title: 'Cookie Preferences',
              acceptAllBtn: 'Accept All',
              acceptNecessaryBtn: 'Reject All',
              savePreferencesBtn: 'Save Preferences',
              closeIconLabel: 'Close',
              sections: [
                {
                  title: 'Cookie Usage',
                  description: 'We use cookies to ensure the basic functionalities of the website and to enhance your online experience.',
                },
                {
                  title: 'Strictly Necessary',
                  description: 'Essential for the website to function properly.',
                  linkedCategory: 'necessary',
                },
                {
                  title: 'Analytics',
                  description: 'Help us understand how visitors interact with our website.',
                  linkedCategory: 'analytics',
                },
                {
                  title: 'Marketing',
                  description: 'Used to deliver relevant advertisements.',
                  linkedCategory: 'marketing',
                },
              ],
            },
          },
        },
      },
    });
    
    console.log('[CookieConsent] Initialized');
  }, []);

  return null;
}

/**
 * Function to programmatically show the preferences modal
 */
export function showCookiePreferences(): void {
  CookieConsent.showPreferences();
}
