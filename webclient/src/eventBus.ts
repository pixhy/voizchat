import { reactive } from "vue";

export const eventBus = reactive({
  showWhiteboard: false,
  whiteboardButtonText: "Whiteboard",
});
