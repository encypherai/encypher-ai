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
});
