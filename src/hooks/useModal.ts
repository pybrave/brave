import { useState } from "react";

type ModalState = {
  key: string | null;
  visible: boolean;
  params?: any;
};

export function useModal() {
  const [modal, setModal] = useState<ModalState>({
    key: null,
    visible: false,
    params: null,
  });

  const openModal = (key: string, params?: any) => {
    setModal({ key, visible: true, params });
  };

  const closeModal = () => {
    setModal({ key: null, visible: false, params: null });
  };

  return { modal, openModal, closeModal };
}

export function useModals(modalKeys: string[]) {
    const [modals, setModals] = useState(
      Object.fromEntries(modalKeys.map((key) => [key, { visible: false, params: null }]))
    );
  
    const openModal = (key: string, params?: any) => {
      setModals((prev) => ({
        ...prev,
        [key]: { visible: true, params },
      }));
    };
  
    const closeModal = (key: string) => {
      setModals((prev) => ({
        ...prev,
        [key]: { visible: false, params: null },
      }));
    };
  
    return { modals, openModal, closeModal };
  }
  