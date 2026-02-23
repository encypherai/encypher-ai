/**
 * Encypher Design System
 * Unified component library for all Encypher properties
 */

// Styles: Import global CSS in the consuming app's entry point (e.g., app/layout.tsx)

// Utils
export { cn } from './utils/cn';

// Components
export { Badge, type BadgeProps } from './components/Badge';
export { Button, type ButtonProps } from './components/Button';
export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  type CardProps,
  type CardHeaderProps,
  type CardTitleProps,
  type CardDescriptionProps,
  type CardContentProps,
  type CardFooterProps,
} from './components/Card';
export { Input, type InputProps } from './components/Input';
export { Switch, type SwitchProps } from './components/Switch';
export { Select, type SelectProps } from './components/Select';
export {
  Tabs,
  TabList,
  Tab,
  TabPanel,
  type TabsProps,
  type TabListProps,
  type TabProps,
  type TabPanelProps,
} from './components/Tabs';
export { Alert, type AlertProps } from './components/Alert';
export { Skeleton, type SkeletonProps } from './components/Skeleton';
export { EmptyState, type EmptyStateProps } from './components/EmptyState';
export { Avatar, type AvatarProps } from './components/Avatar';
