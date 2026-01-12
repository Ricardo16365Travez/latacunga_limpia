export function toErrorMessage(err: any): string {
  try {
    const detail = err?.response?.data?.detail ?? err?.response?.data;
    if (Array.isArray(detail)) {
      const msgs = detail
        .map((d) => (typeof d === 'string' ? d : d?.msg || d?.message))
        .filter(Boolean);
      if (msgs.length) return msgs.join('; ');
    }
    if (detail && typeof detail === 'object') {
      if (detail.msg || detail.message) return String(detail.msg || detail.message);
      return JSON.stringify(detail);
    }
    if (typeof detail === 'string') return detail;
    if (typeof err?.message === 'string') return err.message;
    return 'Ocurrió un error inesperado.';
  } catch {
    return 'Ocurrió un error inesperado.';
  }
}
