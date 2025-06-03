import React from 'react';
import { render, screen } from '@testing-library/react';
import CustomTooltip from './CustomTooltip';

describe('CustomTooltip', () => {
  it('renders null when not active', () => {
    const { container } = render(<CustomTooltip active={false} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders null when payload is empty', () => {
    const { container } = render(<CustomTooltip active={true} payload={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders the tooltip with default formatters', () => {
    const mockPayload = [
      {
        value: 100,
        name: 'Logs',
        dataKey: 'count',
        payload: { date: '2023-01-01', count: 100 }
      }
    ];

    render(
      <CustomTooltip 
        active={true} 
        payload={mockPayload} 
        label="2023-01-01"
      />
    );

    expect(screen.getByText('Date: 2023-01-01')).toBeInTheDocument();
    expect(screen.getByText('Logs: 100')).toBeInTheDocument();
  });

  it('uses custom formatters when provided', () => {
    const mockPayload = [
      {
        value: 1000,
        name: 'Logs',
        dataKey: 'count',
        payload: { date: '2023-01-01', count: 1000 }
      }
    ];

    const formatter = (value: any, name: string) => [`${value.toLocaleString()} items`, `Custom ${name}`];
    const labelFormatter = (label: string) => `Custom Date: ${label}`;

    render(
      <CustomTooltip 
        active={true} 
        payload={mockPayload} 
        label="2023-01-01"
        formatter={formatter}
        labelFormatter={labelFormatter}
      />
    );

    expect(screen.getByText('Custom Date: 2023-01-01')).toBeInTheDocument();
    expect(screen.getByText('Custom Logs: 1,000 items')).toBeInTheDocument();
  });

  it('handles non-numeric values gracefully', () => {
    const mockPayload = [
      {
        value: 'N/A',
        name: 'Status',
        dataKey: 'status',
        payload: { date: '2023-01-01', status: 'N/A' }
      }
    ];

    render(
      <CustomTooltip 
        active={true} 
        payload={mockPayload} 
        label="2023-01-01"
      />
    );

    expect(screen.getByText('Date: 2023-01-01')).toBeInTheDocument();
    expect(screen.getByText('Status: N/A')).toBeInTheDocument();
  });
});
