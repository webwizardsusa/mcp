import ChatFab from './ChatFab';
import ChatPanel from './ChatPanel';
import { useChatPanel } from '../hooks';

/** Floating product-advisor chat launcher + panel. */
const ProductChatWidget = () => {
  const { isOpen, open, close } = useChatPanel();

  return (
    <>
      {!isOpen ? <ChatFab onClick={open} showBadge={false} /> : null}
      <ChatPanel open={isOpen} onClose={close} />
    </>
  );
};

export default ProductChatWidget;
