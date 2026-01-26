/**
 * Gallery Mutations Hook
 * 
 * Re-exports SDK-based gallery mutations for backward compatibility.
 * Consider migrating to direct imports from @/shared/api/hooks/gallery.
 */

export { 
  useCreateGalleryCard as useGalleryMutations,
  useDeleteGalleryCard,
  useReorderGalleryCards,
} from "@/shared/api/hooks/gallery";

// For backward compatibility, also export a combined hook
export function useGalleryMutationsCombined() {
  const { mutate: createCard, ...createRest } = useCreateGalleryCard();
  const { mutate: deleteCard, ...deleteRest } = useDeleteGalleryCard();
  const { mutate: reorderCards, ...reorderRest } = useReorderGalleryCards();

  return {
    createCard: { mutate: createCard, ...createRest },
    deleteCard: { mutate: deleteCard, ...deleteRest },
    reorderCards: { mutate: reorderCards, ...reorderRest },
  };
}

import { useCreateGalleryCard, useDeleteGalleryCard, useReorderGalleryCards } from "@/shared/api/hooks/gallery";
