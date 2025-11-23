'use client';

import Image from 'next/image';
import { useEffect, useRef } from 'react';

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

export default function StandardsCompliance() {
  const slider1Ref = useRef<HTMLDivElement>(null);
  const slider2Ref = useRef<HTMLDivElement>(null);
  
  // Split logos into two halves for different sliders
  const firstHalf = companyLogos.slice(0, Math.ceil(companyLogos.length / 2));
  const secondHalf = companyLogos.slice(Math.ceil(companyLogos.length / 2));
  
  // Double the arrays for seamless looping
  const firstHalfExtended = [...firstHalf, ...firstHalf];
  const secondHalfExtended = [...secondHalf, ...secondHalf];

  useEffect(() => {
    let animationId: number;
    let position1 = 0;
    let position2 = 0;
    
    const logoWidth = 180; // Approximate width of each logo including padding
    const resetPoint1 = firstHalf.length * logoWidth;
    const resetPoint2 = secondHalf.length * logoWidth;
    
    const animate = () => {
      // Slider 1: Right to Left
      position1 -= 0.5; // Adjust speed here
      if (position1 <= -resetPoint1) {
        position1 = 0; // Reset seamlessly
      }
      if (slider1Ref.current) {
        slider1Ref.current.style.transform = `translateX(${position1}px)`;
      }
      
      // Slider 2: Left to Right
      position2 += 0.5; // Adjust speed here
      if (position2 >= resetPoint2) {
        position2 = 0; // Reset seamlessly
      }
      if (slider2Ref.current) {
        slider2Ref.current.style.transform = `translateX(${-resetPoint2 + position2}px)`;
      }
      
      animationId = requestAnimationFrame(animate);
    };
    
    animationId = requestAnimationFrame(animate);
    
    return () => {
      if (animationId) cancelAnimationFrame(animationId);
    };
  }, [firstHalf.length, secondHalf.length]);

  return (
    <section className="py-12 w-full border-t border-border overflow-hidden" style={{backgroundColor: 'rgba(183, 213, 237, 0.3)'}}>
      <div className="container mx-auto px-4">
        <div className="text-center">
          <h3 className="text-2xl font-semibold text-muted-foreground uppercase tracking-wider mb-8">
            We're Authoring the Future of Text Content Authenticity
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
                  className="grayscale hover:grayscale-0 transition-all duration-300"
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
                  className="grayscale hover:grayscale-0 transition-all duration-300"
                />
              </a>
            </div>
          </div>
        </div>
      </div>
      
      {/* Logo Sliders */}
      <div className="relative flex flex-col gap-4">
        <h3 className="text-center text-lg font-semibold text-muted-foreground tracking-wider mb-8">
          Collaborating with the World's Leading Companies
        </h3>
        
        {/* Slider 1 (Right to Left) - First Half */}
        <div className="w-full overflow-hidden whitespace-nowrap">
          <div 
            ref={slider1Ref}
            className="flex items-center"
            style={{ willChange: 'transform' }}
          >
            {firstHalfExtended.map((logo, index) => (
              <div key={`rtl-${index}`} className="inline-flex items-center justify-center px-10 flex-shrink-0 opacity-60">
                <Image
                  src={`/c2pa_companies/${logo}`}
                  alt={`${logo.split('.')[0]} logo`}
                  height={40}
                  width={100}
                  style={{objectFit: "contain"}}
                  className="grayscale"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Slider 2 (Left to Right) - Second Half */}
        <div className="w-full overflow-hidden whitespace-nowrap">
          <div 
            ref={slider2Ref}
            className="flex items-center"
            style={{ willChange: 'transform' }}
          >
            {secondHalfExtended.map((logo, index) => (
              <div key={`ltr-${index}`} className="inline-flex items-center justify-center px-10 flex-shrink-0 opacity-60">
                <Image
                  src={`/c2pa_companies/${logo}`}
                  alt={`${logo.split('.')[0]} logo`}
                  height={40}
                  width={100}
                  style={{objectFit: "contain"}}
                  className="grayscale"
                />
              </div>
            ))}
          </div>
        </div>
        
        {/* Gradient overlay for fade effect */}
        {/* <div className="absolute inset-0 bg-gradient-to-r from-[rgba(183,213,237,0.3)] via-transparent to-[rgba(183,213,237,0.3)] pointer-events-none"></div> */}
      </div>
    </section>
  );
}