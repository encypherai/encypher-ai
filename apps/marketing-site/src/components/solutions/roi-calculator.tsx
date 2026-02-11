"use client";

import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

export default function RoiCalculator() {
  const [articleCount, setArticleCount] = useState(5000);
  const [infringementRate, setInfringementRate] = useState(15);
  const [avgLicensingFee, setAvgLicensingFee] = useState(250);

  const potentialRevenue = useMemo(() => {
    const infringedArticles = articleCount * (infringementRate / 100);
    return infringedArticles * avgLicensingFee;
  }, [articleCount, infringementRate, avgLicensingFee]);

  return (
    <Card className="w-full max-w-4xl mx-auto shadow-2xl border-border">
      <CardHeader>
        <CardTitle className="text-2xl md:text-3xl text-center">Estimate Your Potential Licensing Revenue</CardTitle>
      </CardHeader>
      <CardContent className="p-6 md:p-8">
        <div className="grid md:grid-cols-2 gap-8 lg:gap-12">
          <div className="space-y-6">
            <div>
              <label htmlFor="article-count" className="block text-sm font-medium text-muted-foreground mb-2">
                Number of Published Articles
              </label>
              <div className="flex items-center gap-4">
                <Slider
                  id="article-count"
                  min={100}
                  max={50000}
                  step={100}
                  value={[articleCount]}
                  onValueChange={(value: number[]) => setArticleCount(value[0])}
                />
                <Input
                  type="number"
                  className="w-28 font-bold"
                  value={articleCount}
                  onChange={(e) => setArticleCount(Number(e.target.value))}
                />
              </div>
            </div>
            <div>
              <label htmlFor="infringement-rate" className="block text-sm font-medium text-muted-foreground mb-2">
                Estimated Infringement Rate (%)
              </label>
              <div className="flex items-center gap-4">
                <Slider
                  id="infringement-rate"
                  min={1}
                  max={50}
                  step={1}
                  value={[infringementRate]}
                  onValueChange={(value: number[]) => setInfringementRate(value[0])}
                />
                <Input
                  type="number"
                  className="w-28 font-bold"
                  value={infringementRate}
                  onChange={(e) => setInfringementRate(Number(e.target.value))}
                />
              </div>
            </div>
            <div>
              <label htmlFor="licensing-fee" className="block text-sm font-medium text-muted-foreground mb-2">
                Average Licensing Fee per Article
              </label>
              <div className="flex items-center gap-4">
                <Slider
                  id="licensing-fee"
                  min={50}
                  max={2000}
                  step={10}
                  value={[avgLicensingFee]}
                  onValueChange={(value: number[]) => setAvgLicensingFee(value[0])}
                />
                <Input
                  type="number"
                  className="w-28 font-bold"
                  value={avgLicensingFee}
                  onChange={(e) => setAvgLicensingFee(Number(e.target.value))}
                />
              </div>
            </div>
          </div>

          <div className="bg-muted/50 rounded-lg p-6 flex flex-col items-center justify-center text-center border border-dashed border-border">
            <h3 className="text-lg font-semibold text-muted-foreground">Gross Licensing Opportunity</h3>
            <p className="text-4xl md:text-5xl font-bold text-primary my-2">
              {formatCurrency(potentialRevenue)}
            </p>
            <p className="text-xs text-muted-foreground max-w-xs mt-3">
              Any resulting licensing revenue is shared between the coalition and the publisher, with the majority going to the content creator.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
