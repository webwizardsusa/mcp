import ChatFab from './ChatFab';
import ChatPanel from './ChatPanel';
import { useChatPanel } from '../hooks';

/** Floating chat launcher + panel (UI only; no AI backend yet). */
const ProductChatWidget = () => {
  const { isOpen, open, close } = useChatPanel();

  return (
    <>
      {!isOpen ? <ChatFab onClick={open} /> : null}
      <ChatPanel open={isOpen} onClose={close} />
    </>
  );
};

export default ProductChatWidget;
