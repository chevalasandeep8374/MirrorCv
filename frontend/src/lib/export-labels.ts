/**
 * Standard labels and disclaimer copy for resume exports.
 * Rule: Editor DOCX export is labeled as "Simplified Word Export" with a note on differences;
 * PDF is the faithful download.
 */

export const EXPORT_LABELS = {
  pdf: {
    title: 'Download PDF',
    badge: 'Recommended',
    description: 'Exact visual layout, typography, and page breaks. Best for job applications.',
  },
  docx: {
    title: 'Simplified Word Export (.docx)',
    badge: 'Editable',
    description:
      'Simplified formatting for editing text in Microsoft Word. Note: Exact margins, complex columns, and custom font metrics may differ from preview.',
  },
  json: {
    title: 'Export JSON',
    badge: 'Raw Data',
    description: 'Portable resume content and style tokens schema v1.1.0.',
  },
  txt: {
    title: 'Plain Text (.txt)',
    badge: 'Raw Text',
    description: 'Unformatted plain text for quick copy-pasting into text boxes.',
  },
} as const;
