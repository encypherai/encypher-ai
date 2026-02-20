import { renderBlogMarkdown } from './blog';

describe('renderBlogMarkdown', () => {
  it('renders markdown tables into semantic HTML table elements', async () => {
    const markdown = [
      '| Publisher | AI Company | Deal Type |',
      '| --- | --- | --- |',
      '| AP | OpenAI | Training + news access |',
      '| FT | OpenAI | Training + citation |',
    ].join('\n');

    const html = await renderBlogMarkdown(markdown);

    expect(html).toContain('<table>');
    expect(html).toContain('<thead>');
    expect(html).toContain('<tbody>');
    expect(html).toContain('<th>Publisher</th>');
    expect(html).toContain('<td>AP</td>');
  });

  it('preserves inline invisible variation selector markers', async () => {
    const marker = String.fromCodePoint(0xe0100);
    const markdown = `Hello${marker} world`;

    const html = await renderBlogMarkdown(markdown);

    expect(html).toContain(marker);
  });

  it('preserves trailing invisible variation selector markers', async () => {
    const marker = String.fromCodePoint(0xe0100);
    const trailingMarkers = `${marker}${marker}${marker}`;
    const markdown = `Line one.\n\nLine two.${trailingMarkers}`;

    const html = await renderBlogMarkdown(markdown);

    expect(html).toContain(trailingMarkers);
  });
});
