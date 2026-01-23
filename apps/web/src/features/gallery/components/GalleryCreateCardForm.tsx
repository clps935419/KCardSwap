"use client";

import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

interface GalleryCreateCardFormProps {
  onSuccess?: () => void;
}

interface CreateCardFormData {
  title: string;
  idol_name: string;
  era?: string;
  description?: string;
}

export function GalleryCreateCardForm({ onSuccess }: GalleryCreateCardFormProps) {
  const form = useForm<CreateCardFormData>({
    defaultValues: {
      title: "",
      idol_name: "",
      era: "",
      description: "",
    },
  });

  const onSubmit = async (data: CreateCardFormData) => {
    try {
      const response = await fetch("/api/v1/gallery/cards", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          title: data.title,
          idol_name: data.idol_name,
          era: data.era || undefined,
          description: data.description || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create card");
      }

      onSuccess?.();
      form.reset();
    } catch (error) {
      console.error("Error creating card:", error);
      form.setError("root", {
        message: error instanceof Error ? error.message : "Failed to create card",
      });
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="title"
          rules={{ required: "Title is required", maxLength: { value: 200, message: "Title is too long" } }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title *</FormLabel>
              <FormControl>
                <Input placeholder="Card title" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="idol_name"
          rules={{ required: "Idol name is required", maxLength: { value: 100, message: "Idol name is too long" } }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Idol Name *</FormLabel>
              <FormControl>
                <Input placeholder="e.g., IU" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="era"
          rules={{ maxLength: { value: 100, message: "Era is too long" } }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Era (Optional)</FormLabel>
              <FormControl>
                <Input placeholder="e.g., Love Poem" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          rules={{ maxLength: { value: 1000, message: "Description is too long" } }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description (Optional)</FormLabel>
              <FormControl>
                <Textarea 
                  placeholder="Add a description..."
                  rows={3}
                  {...field} 
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {form.formState.errors.root && (
          <div className="text-sm text-destructive">
            {form.formState.errors.root.message}
          </div>
        )}

        <div className="flex justify-end gap-2">
          <Button
            type="submit"
            disabled={form.formState.isSubmitting}
          >
            {form.formState.isSubmitting ? "Creating..." : "Create Card"}
          </Button>
        </div>
      </form>
    </Form>
  );
}
