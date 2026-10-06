import { crud } from './crud';
// Admin's shops. Backend must return only shops owned by the logged-in admin.
export const shopService = crud('/shops');
