
function handleCode (code, isWeb) {
  if (isWeb) {
    return code;
  }
  // 要插入的滚动条样式
  const scrollbarStyle = `
  <style>
    ::-webkit-scrollbar {
        width: 0px;
    }
  </style>
  `;

  // 将样式插入到 <head> 标签内（如果存在 <head>）
  let modifiedHtml = code;
  if (/\s*<\/head\s*>/i.test(modifiedHtml)) {
    modifiedHtml = modifiedHtml.replace(/(\s*<\/head\s*>)/i, `${scrollbarStyle}$1`);
  } else {
  // 如果没有 <head>，直接插入到 <html> 之后
    modifiedHtml = modifiedHtml.replace('<html>', `<html>${scrollbarStyle}`);
  }
  return modifiedHtml
}


const useEventListener = (element, eventType, callback, useCapture = false) => {
  if (!element || !callback) return null;

  const handler = (event) => callback(event);
  element.addEventListener(eventType, handler, useCapture);

  return () => {
    element.removeEventListener(eventType, handler, useCapture);
  };
};