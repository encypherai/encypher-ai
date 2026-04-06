'use client';

import Image from 'next/image';
import styles from './StandardsCompliance.module.css';

const companyLogos = [
  'akamai_technologies_inc_1743684419708_0014100000TdzWHAAZ.svg',
  'amazon_1342_1744836899930_001QP00000IikpZYAR.svg',
  'arm-limited.svg',
  'associatedpress.svg',
  'Bank-of-America-logo.svg',
  'bbc.svg',
  'deloitte-consulting-llp.svg',
  'digicert-inc.svg',
  'electronicarts.svg',
  'fujifilm_corporation_1716032580703_0012M00002XjzMBQAZ.svg',
  'google-llc.svg',
  'infosys-limited.svg',
  'intel-corporation.svg',
  'meta_platforms_inc_1714768245542_0014100000TdzwSAAR.svg',
  'microsoft-corporation.svg',
  'new-york-times.svg',
  'nhk.svg',
  'OpenAIInc.svg',
  'partnership-on-ai.svg',
  'publicis-groupe.svg',
  'qualcomm-inc.svg',
  'samsung_electronics_co._ltd._1700625975816_0014100000Te0dPAAR.svg',
  'sony-corporation.svg',
  'ssl-inc.svg',
  'TikTokInc..svg',
  'truepic_inc_1750791251442_0012M00002QWFDVQA5.svg',
  'witness.svg',
  'adobe_inc_1714766282443_0014100000Te1FFAAZ.svg'
];

// Split logos into two halves for different sliders
const firstHalf = companyLogos.slice(0, Math.ceil(companyLogos.length / 2));
const secondHalf = companyLogos.slice(Math.ceil(companyLogos.length / 2));

export default function StandardsCompliance() {
  return (
    <section className="py-12 w-full border-t border-border overflow-hidden bg-columbia-blue/30 dark:bg-slate-800/50">
      <div className="container mx-auto px-4">
        <div className="text-center">
          <h3 className="text-2xl font-semibold text-muted-foreground uppercase tracking-wider mb-8">
            We&apos;re Authoring the Future of Content Authenticity
          </h3>
          <div className="flex justify-center items-center gap-12 md:gap-16 mb-8">
            <div className="relative h-12 w-48">
              <a href="https://c2pa.org" target="_blank" rel="noopener noreferrer">
                <Image
                  src="/c2pa-hero.svg"
                  alt="C2PA Logo"
                  fill
                  sizes="192px"
                  style={{objectFit: "contain"}}
                  className="grayscale hover:grayscale-0 transition-all duration-300 dark:invert"
                />
              </a>
            </div>
            <div className="relative h-12 w-48">
              <a href="https://contentauthenticity.org" target="_blank" rel="noopener noreferrer">
                <Image
                  src="/CAI_Lockup_RGB_Black.svg"
                  alt="Content Authenticity Initiative Logo"
                  fill
                  sizes="192px"
                  style={{objectFit: "contain"}}
                  className="grayscale hover:grayscale-0 transition-all duration-300 dark:invert"
                />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Logo Sliders - CSS Animation for smooth infinite scroll */}
      <div className="relative flex flex-col gap-6">
        <h3 className="text-center text-lg font-semibold text-muted-foreground tracking-wider mb-4">
          Encypher co-chairs the C2PA Text Provenance Task Force and implements the standard across all media. Building content authenticity together.
        </h3>

        {/* Slider 1 (Right to Left) */}
        <div className={styles.logoSlider}>
          <div className={`${styles.sliderTrack} ${styles.scrollRtoL}`}>
            {/* Render logos twice for seamless loop */}
            {[...firstHalf, ...firstHalf].map((logo: string, index: number) => (
              <div key={`rtl-${index}`} className={styles.logo}>
                <Image
                  src={`/c2pa_companies/${logo}`}
                  alt={`${logo.split('.')[0]} logo`}
                  height={40}
                  width={120}
                  style={{ objectFit: 'contain', width: 'auto', height: 40 }}
                  className="grayscale dark:invert"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Slider 2 (Left to Right) */}
        <div className={styles.logoSlider}>
          <div className={`${styles.sliderTrack} ${styles.scrollLtoR}`}>
            {/* Render logos twice for seamless loop */}
            {[...secondHalf, ...secondHalf].map((logo: string, index: number) => (
              <div key={`ltr-${index}`} className={styles.logo}>
                <Image
                  src={`/c2pa_companies/${logo}`}
                  alt={`${logo.split('.')[0]} logo`}
                  height={40}
                  width={120}
                  style={{ objectFit: 'contain', width: 'auto', height: 40 }}
                  className="grayscale dark:invert"
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
