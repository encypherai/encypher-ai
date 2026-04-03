/**
 * Encypher Design System v2.0.0
 * Unified component library for all Encypher properties
 *
 * Built on shadcn/ui + Radix UI primitives with Encypher brand tokens.
 */

// Utils
export { cn } from './utils/cn';

// --- Core Components ---

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from './components/accordion';
export { Alert, AlertTitle, AlertDescription } from './components/alert';
export { Badge, badgeVariants, type BadgeProps } from './components/badge';
export { Button, buttonVariants, type ButtonProps } from './components/button';
export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent,
} from './components/card';
export {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogOverlay,
  DialogPortal,
  DialogTitle,
  DialogTrigger,
} from './components/dialog';
export {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from './components/dropdown-menu';
export {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  useFormField,
} from './components/form';
export { Input } from './components/input';
export { Label } from './components/label';
export { RadioGroup, RadioGroupItem } from './components/radio-group';
export { ScrollArea, ScrollBar } from './components/scroll-area';
export {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectScrollDownButton,
  SelectScrollUpButton,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from './components/select';
export { Separator } from './components/separator';
export {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from './components/sheet';
export { Skeleton } from './components/skeleton';
export { Slider } from './components/slider';
export { Toaster } from './components/sonner';
export { Switch } from './components/switch';
export {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from './components/table';
export { Tabs, TabsList, TabsTrigger, TabsContent } from './components/tabs';
export { Textarea } from './components/textarea';
export { Toggle, toggleVariants } from './components/toggle';
export {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './components/tooltip';
export { useToast, ToastProvider } from './components/use-toast';

// --- Legacy Components (no shadcn equivalent) ---

export { EmptyState, type EmptyStateProps } from './components/EmptyState';
export { Avatar, type AvatarProps } from './components/Avatar';
