// __tests__/Card.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import Card from '../Card';

describe('Card Component', () => {
  it('should render children correctly', () => {
    const childText = 'This is the card content';
    render(<Card><p>{childText}</p></Card>);
    expect(screen.getByText(childText)).toBeInTheDocument();
  });

  it('should apply base and custom className', () => {
    const customClass = 'my-custom-card';
    const { container } = render(<Card className={customClass}><p>Content</p></Card>);
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('card');
    expect(cardElement).toHaveClass(customClass);
  });

  it('should render title when provided', () => {
    const titleText = 'Card Title';
    render(<Card title={titleText}><p>Content</p></Card>);
    expect(screen.getByRole('heading', { name: titleText, level: 2 })).toBeInTheDocument();
  });

  it('should render headerContent when provided', () => {
    const headerText = 'Extra Header Info';
    render(<Card headerContent={<span>{headerText}</span>}><p>Content</p></Card>);
    expect(screen.getByText(headerText)).toBeInTheDocument();
  });

  it('should render both title and headerContent when both are provided', () => {
    const titleText = 'Main Title';
    const headerText = 'Subtitle Info';
    render(
      <Card title={titleText} headerContent={<span>{headerText}</span>}>
        <p>Content</p>
      </Card>
    );
    expect(screen.getByRole('heading', { name: titleText, level: 2 })).toBeInTheDocument();
    expect(screen.getByText(headerText)).toBeInTheDocument();
  });

  it('should not render header section if title and headerContent are not provided', () => {
    render(<Card><p>Content</p></Card>);
    // Check that no h2 (for title) or the div for headerContent is rendered.
    // The header section has a 'mb-4' class.
    const headerDiv = screen.queryByText((content, element) => {
      return element?.tagName.toLowerCase() === 'div' && element.classList.contains('mb-4');
    });
    expect(headerDiv).not.toBeInTheDocument();
  });
});
