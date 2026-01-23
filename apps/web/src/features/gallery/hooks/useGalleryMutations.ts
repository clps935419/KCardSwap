import { useMutation, useQueryClient } from "@tanstack/react-query";

// TODO: Replace with generated SDK once OpenAPI is updated

async function createGalleryCard(data: {
  title: string;
  idol_name: string;
  era?: string;
  description?: string;
}) {
  const response = await fetch("/api/v1/gallery/cards", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Failed to create gallery card");
  }

  return response.json();
}

async function deleteGalleryCard(cardId: string) {
  const response = await fetch(`/api/v1/gallery/cards/${cardId}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to delete gallery card");
  }

  return true;
}

async function reorderGalleryCards(cardIds: string[]) {
  const response = await fetch("/api/v1/gallery/cards/reorder", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ card_ids: cardIds }),
  });

  if (!response.ok) {
    throw new Error("Failed to reorder gallery cards");
  }

  return response.json();
}

export function useGalleryMutations() {
  const queryClient = useQueryClient();

  const createCard = useMutation({
    mutationFn: createGalleryCard,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-gallery"] });
    },
  });

  const deleteCard = useMutation({
    mutationFn: deleteGalleryCard,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-gallery"] });
    },
  });

  const reorderCards = useMutation({
    mutationFn: reorderGalleryCards,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-gallery"] });
    },
  });

  return {
    createCard,
    deleteCard,
    reorderCards,
  };
}
