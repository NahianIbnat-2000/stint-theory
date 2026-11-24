import { useState } from "react";

// Hover layer shared by the charts: call show(evt, content) / hide().
export function useTooltip() {
  const [tip, setTip] = useState(null);
  const show = (e, content) => {
    const box = e.currentTarget.ownerSVGElement?.parentNode?.getBoundingClientRect() ??
      e.currentTarget.parentNode.getBoundingClientRect();
    setTip({ x: e.clientX - box.left, y: e.clientY - box.top, content });
  };
  const hide = () => setTip(null);
  const node = tip && (
    <div className="tooltip" style={{ left: tip.x + 14, top: tip.y + 10 }} role="status">{tip.content}</div>
  );
  return { show, hide, node };
}
