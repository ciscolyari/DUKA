// Text translation is done at runtime by src/i18n (English text -> Kiswahili).
// t() only fills {placeholders}, so strings stay valid English in the code.
export const t = (s, vars) => (typeof s !== 'string' || !vars ? s : s.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? ''));
