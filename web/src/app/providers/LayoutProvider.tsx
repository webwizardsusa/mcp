import { useEffect, type ReactNode } from 'react';
import { layoutConfig } from './config';

type Props = {
  children: ReactNode;
};

export const LayoutProvider = ({ children }: Props) => {
  useEffect(() => {
    document.documentElement.setAttribute('class', 'light');
    document.documentElement.setAttribute('dir', layoutConfig.direction);
    document.documentElement.setAttribute('data-layout', 'vertical');
  }, []);

  return children;
};
