/**
 * Utility functions to clean and format AI-generated content
 */

/**
 * Removes markdown asterisks and other formatting characters from text
 * while preserving the text content
 */
export function cleanMarkdownFormatting(text) {
  if (!text) return '';
  
  return text
    // Remove bold/italic markers (**, *, ___, __)
    .replace(/\*\*\*/g, '')
    .replace(/\*\*/g, '')
    .replace(/\*/g, '')
    .replace(/___/g, '')
    .replace(/__/g, '')
    // Clean up extra whitespace that might result
    .replace(/  +/g, ' ')
    .trim();
}

/**
 * Formats content for display, converting markdown-style formatting
 * to clean, readable text with proper structure
 */
export function formatContentForDisplay(content) {
  if (!content) return '';
  
  return content
    // Remove bold/italic markers but keep the text
    .replace(/\*\*\*([^*]+)\*\*\*/g, '$1')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/___([^_]+)___/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    // Replace standalone asterisks used as bullet points
    .replace(/^\* /gm, '• ')
    // Clean up any remaining stray asterisks
    .replace(/\*/g, '')
    .trim();
}

/**
 * Formats content for PDF export, cleaning up markdown
 * and preparing text for document rendering
 */
export function formatContentForPDF(content) {
  if (!content) return '';
  
  return content
    // Convert markdown headers to plain text with newlines
    .replace(/^#{1,6}\s+(.+)$/gm, '\n$1\n')
    // Remove bold/italic markers
    .replace(/\*\*\*([^*]+)\*\*\*/g, '$1')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/___([^_]+)___/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    // Convert asterisk bullets to proper bullets
    .replace(/^\* /gm, '• ')
    // Clean up any remaining stray asterisks
    .replace(/\*/g, '')
    // Normalize multiple newlines
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}
