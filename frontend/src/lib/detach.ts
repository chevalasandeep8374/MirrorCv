import { Resume } from '@/types/resume';
import { ResumeStyle } from '@/types/style';

/**
 * Detaches an uploaded DOCX/PDF resume from its template lock:
 * 1. Clones the existing resume into a NEW resume.
 * 2. Sets sourceType to 'editor'.
 * 3. Preserves extracted style tokens as a "Custom (from your upload)" design.
 * 4. Clears isLocked (unlocks full design customization).
 * 5. Returns the new detached resume payload.
 */
export function detachResumeFromTemplate(originalResume: Resume): Partial<Resume> {
  const detachedStyle: ResumeStyle = {
    ...JSON.parse(JSON.stringify(originalResume.style)),
    templateId: 'custom-from-upload',
    isLocked: false,
  };

  return {
    title: `${originalResume.title} (Custom Design)`,
    content: JSON.parse(JSON.stringify(originalResume.content)),
    style: detachedStyle,
    sourceType: 'editor',
    source_type: 'editor',
    version: 1,
  };
}
