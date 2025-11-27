import { z } from "zod";

export const orgUpdateSchema = z.object({
  name: z.string().min(2, "Organization name is required").max(100, "Name too long"),
  contactEmail: z.string().email("Invalid email address"),
  address: z.string().max(400, "Address too long").optional(),
});

export type OrgUpdateInput = z.infer<typeof orgUpdateSchema>;
